import { images } from '../../constants'

// Sender
export const sender = {
    "name": "Ironman",
    "uid": "user1",
    "avatar": "https://drive.google.com/uc?export=view&id=1z9STRaug7WwlyJ3qVMLsgQFW3wQAmAbd"
}

export const agent = {
    "name": "MUKALMA",
    "uid": "user2",
    "avatar": images.splashLogo
}

// Storing Messages
export const initialState = [
    {
    "text": "Hello! I am MUKALMA, An Intelligent Q/A Chatbot",
    "id": "1",
    "sender": agent
    },
]
