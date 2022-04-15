import React, { useState, useEffect } from 'react'
import { useDispatch } from 'react-redux';

import { sendMessage, waitForResponse } from '../../actions/message'
import { sender } from './state';

import MessageList from './MessageList/MessageList'

import { Mic, MicNone } from '@material-ui/icons';
import { IconButton } from '@mui/material';

import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import useSound from 'use-sound';

import { audio } from '../../constants'
import './styles.css';
import ResponseProgress from './ResponseProgress/ResponseProgress';

// Scrolling to bottom function
export const scrollToBottom = () => {
    var endOfChat = document.getElementById('end-of-chat');
    endOfChat.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});
}

const Chatbox = ({ messages, setMessages, setSource, setSpanSelected, setResponses, setSpeechText }) => {
    // Dispatcher
    const dispatch = useDispatch();

    // State
    const [message, setMessage] = useState('');
    const [width, setWidth] = useState(window.innerWidth)

    window.addEventListener('resize', function(event) {
        setWidth(window.innerWidth)
    })

    // Stepper Padding Size code
    const paddingValues = ['50px', '10px']
    const [paddingBottom, setPaddingBottom] = useState(0)
    var numMessages = 1;

    // Progress
    const [showProgress, setShowProgress] = useState(false);
    const [responseProgressMessage, setResponseProgressMessage] = useState('Fetching knowledge source ...');
    const [activeStep, setActiveStep] = useState(0);
    
    // Microphone State
    const {
      transcript,
      listening
    } = useSpeechRecognition();

    // Audio State
    const [ playMicStartSound ] = useSound(audio.micStart);
    const [ playMicStopSound ] = useSound(audio.micStop);
  
    // Use Effects
    // When the transcript changes
    useEffect(() => {
        setMessage(transcript);
    }, [transcript])
    
    // Function to handle onSubmitMessage
    const onSubmitMessage = (message) => {

        // Adding the message to the list
        setMessages(messages => [...messages, {
            "text": message,
            "id": "0",
            "sender": sender
        }])
        setPaddingBottom(1);

        // Making progress bar visible
        console.log("Changing ProgressBar to True")
        setShowProgress(true)

        // Dispatching Network calls
        // For Message
        dispatch(sendMessage(
            {"message": message}
        ))

        // For Progress
        setTimeout(() => {
            dispatch(waitForResponse( 
                setMessages,
                setSource, 
                setSpanSelected, 
                setResponses, 
                setSpeechText,
                messages,
                setShowProgress,
                setPaddingBottom,
                setResponseProgressMessage,
                setActiveStep
            ));
        }, 500)
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
        playMicStartSound();
        SpeechRecognition.startListening()
    }

    // When listening stops
    useEffect(() => {
        if (!listening && message.length) {
            playMicStopSound();
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
                    { showProgress ? 
                        <ResponseProgress 
                            responseProgressMessage={responseProgressMessage}
                            activeStep={activeStep}/>
                        :
                        <></>
                    }
                    <div id="end-of-chat" style={{ paddingBottom: paddingValues[paddingBottom] }}/>
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
                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                                {listening ? (
                                    <>
                                        <div className='pulse-ring' />
                                        <Mic className='mic-icon'/>
                                    </>
                                ) : <MicNone className='mic-icon'/>}
                            </div>
                        </IconButton>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Chatbox
