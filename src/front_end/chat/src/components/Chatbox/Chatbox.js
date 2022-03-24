import React, { useState, useEffect } from 'react'
import { useDispatch } from 'react-redux';

import { sendMessage } from '../../actions/message'
import { sender } from './state';

import TypingIndicator from './TypingIndicator/TypingIndicator'
import { setTyping } from './TypingIndicator/setTyping';
import MessageList from './MessageList/MessageList'

import { Mic, MicNone } from '@material-ui/icons';
import { IconButton } from '@mui/material';

import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

import './styles.css';

// Scrolling to bottom function
export const scrollToBottom = () => {
    var endOfChat = document.getElementById('end-of-chat');
    endOfChat.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});
}

const Chatbox = ({ messages, setMessages, setSpanSelected, setResponses, setSpeechText }) => {
    // Dispatcher
    const dispatch = useDispatch();

    // State
    const [message, setMessage] = useState('');

    // Using a state for tracking width
    const [width, setWidth] = useState(window.innerWidth)

    window.addEventListener('resize', function(event) {
        setWidth(window.innerWidth)
    })
    
    // Microphone State
    const {
      transcript,
      listening
    } = useSpeechRecognition();
  
    // When the transcript changes
    useEffect(() => {
        setMessage(transcript);
    }, [transcript])
    
    // Function to handle onSubmitMessage
    const onSubmitMessage = (message) => {
        setTyping();
        setMessages(messages => [...messages, {
            "text": message,
            "id": "0",
            "sender": sender
        }])
        dispatch(sendMessage(
            {"message": message}, 
            setMessages, 
            setSpanSelected, 
            setResponses, 
            setSpeechText,
            messages
        ));
    }

    // Submit Function
    const handleSubmit = (event) => {
        if (event) {
            event.preventDefault();
        }
        var msg = message;

        onSubmitMessage(msg);
        setMessage('');
    }

    useEffect(() => {
        scrollToBottom(messages.length);
    }, [messages])

    // Toggle between listening states
    const toggleListening = () => {
        console.log("Listening Started")
        SpeechRecognition.startListening()
    }

    // When listening stops
    useEffect(() => {
        if (!listening && message.length) {
            handleSubmit();
        }
    }, [listening])

    // Building HTML
    return (
        <div className='chat-box'>
            <div className='msg-page'>
                <MessageList 
                    messages={messages}
                    isLoading={false}
                    user={{"uid": "user1"}}
                />
                <div className='chat-box-bottom'>
                    <TypingIndicator />
                    <div id="end-of-chat" />
                </div>
            </div>
            <div className='msg-footer'>
                <form className='message-form' onSubmit={handleSubmit} id="form">
                    <div className='input-group'>
                        <input
                            type='text'
                            className='form-control message-input'
                            placeholder='Type something'
                            value={message}
                            onChange={(event) => setMessage(event.target.value)}
                            required={true}
                        />
                        <IconButton onClick={toggleListening} style={{ marginRight: "10px" }}>
                            {listening ? <Mic /> : <MicNone />}
                        </IconButton>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Chatbox
