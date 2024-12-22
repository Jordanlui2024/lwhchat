import json
import time

from datetime import datetime
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache

from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.room_group_name = 'chat_%s'% self.room_name
        self.rooms_count_joiner = "rooms_count"
        
        room_count = cache.get(self.rooms_count_joiner, {})
        joiners = cache.get(self.room_group_name, [])
        
        """---------------------- this for the rooms count joiners ---------------"""
        if self.room_name == "rooms_count" : 
            await self.channel_layer.group_add(
                self.rooms_count_joiner,
                self.channel_name
            )            
        else:    
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            ) 
            room_count[self.room_name] = room_count.get(self.room_name,0) + 1
            cache.set(self.rooms_count_joiner, room_count)
            """------------------for the room get all joiners name-------------------- """
            if self.user_name not in joiners:
               joiners.append(self.user_name)
               cache.set(self.room_group_name, joiners)
            
            #print(f"send {joiners}")
            await self.channel_layer.group_send(
                self.room_group_name,
                    {
                     'type':'chat_logout',
                     'joiners': joiners
                    }
            )
               
        
        if len(room_count) > 0:
            await self.channel_layer.group_send(
                self.rooms_count_joiner,
                {
                    'type':"rooms_count_send",
                    'count':room_count
                }
            )
        
        await self.accept()


        
    async def rooms_count_send(self, event):
        time.sleep(0.5)
        count = event['count']
        await self.send(text_data=json.dumps({
            'count':count
        })) 
           
    async def chat_logout(self, event):
        time.sleep(0.5)
        joiners = event['joiners']
        # print(f"send2 {joiners}")
        await self.send(text_data=json.dumps({
            'joiners':joiners
        }))
        
        
        
    async def disconnect(self, code):
        if self.room_name != "rooms_count":
            room_count = cache.get(self.rooms_count_joiner, {})
            room_count[self.room_name] = room_count.get(self.room_name,0)-1
            if room_count[self.room_name] < 0 :
                room_count[self.room_name] = 0
                
            cache.set(self.rooms_count_joiner, room_count)
            
            await self.channel_layer.group_send( # send rooms count joinner
                self.rooms_count_joiner,
                {
                    'type':'rooms_count_send',
                    'count':room_count
                }
            )
            """------------------------------ for joiners name display remove-----------------------"""
            joiners = cache.get(self.room_group_name, [])
            
            if self.user_name in joiners: 
                joiners.remove(self.user_name)
                cache.set(self.room_group_name, joiners)
                await self.channel_layer.group_send(
                    self.room_group_name,
                       {
                        'type':'chat_logout',
                        'joiners': joiners
                       }
                )
                
     
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
        else:
            await self.channel_layer.group_discard(
                self.rooms_count_joiner,
                self.channel_name
            )    
        # self.close(code)    
        
        
    async def receive(self, text_data):
        data=json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']
        now = datetime.now()
        date = now.strftime("%H:%M")
        if len(message) > 0 :
           await self.save_message(username, room, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'username':username,
                'date':date
            }
        )
        
        
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        date = event['date']
        await self.send(text_data=json.dumps({
            'message':message,
            'username':username,
            'date':date
        }))    
        
    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username = username)
        room = Room.objects.get(slug=room)
        Message.objects.create(user=user, room=room, content=message)    
            