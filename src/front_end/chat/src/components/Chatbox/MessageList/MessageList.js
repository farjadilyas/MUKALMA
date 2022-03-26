import React, { useEffect, useState } from 'react'
import MDSpinner from 'react-md-spinner';
import { motion, AnimatePresence } from 'framer-motion'

const MessageList = ({ messages, isLoading, user }) => {

    // State variable for animation changing
    const [yValue, setYValue] = useState(0);

    // Motion preset
    const transition = {
        type: 'spring',
        stiffness: 200,
        mass: 0.2,
        damping: 20,
    }
      
    const variants = {
        initial: {
          opacity: 0,
          y: yValue,
        },
        enter: {
          opacity: 1,
          y: 0,
          transition,
        },
    }

    // Using mount effect to change animation Y
    useEffect(() => {
        setYValue(300);
    }, [])
    
    // Using a state for tracking width
    const [width, setWidth] = useState(window.innerWidth)

    window.addEventListener('resize', function(event) {
        setWidth(window.innerWidth)
    })

    // Building Layout
    var chatContent = (
        <div className='loading-messages-container'>
            <MDSpinner size={100}/>
            <span className='loading-text'>Loading Messages</span>
        </div>
    );

    if (!isLoading && messages.length) return (
        // Mapping each message into a bubble
        chatContent = messages.map((message, index) => {
            // Depending on the user, we display the sender's name component
            var isUser = user.uid === message.sender.uid;
            var renderName = void 0;
            if (isUser) {
                renderName = (<></>);
            } else {
                renderName = (
                    <div className='sender-name'>{message.sender.name}</div>
                );
            }

            // Building the complete Message layout
            return (
                <motion.li
                    key={message.id}
                    initial="initial"
                    animate="enter"
                    variants={variants}
                    layout
                    id={`message-bubble-${index}`} 
                    className="chat-bubble-row"
                    style={{ flexDirection: isUser ? 'row-reverse' : 'row' }}
                >
                    <div>  
                        {!isUser && width > 600 ? (
                            <img 
                                src={message.sender.avatar}
                                alt="sender avatar"
                                className='avatar'
                                style={ isUser ? { marginLeft: '15px' } : { marginRight: '5px' }} 
                            />
                        ) : ''}
                        <div className={'chat-bubble ' + (isUser ? 'is-user' : 'is-other')}>
                            {renderName}
                            <div className='message' style={{ color: isUser ? '#FFF' : '#2D313F' }}>
                                {message.text}
                            </div>
                            <div>
                                <p 
                                    className='timestamp' 
                                    style={ isUser ? { color: 'white' } : {} }
                                >
                                    {new Date().toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true })}
                                </p>
                            </div>
                        </div>
                    </div>
                </motion.li>
            );
        })
    );
}

export default MessageList
