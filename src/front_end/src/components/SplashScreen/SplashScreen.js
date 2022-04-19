import React from 'react'

import { images } from '../../constants'
import { Typography } from '@material-ui/core'
import { motion } from 'framer-motion'

import './styles.css'

const SplashScreen = () => {
    // Defining text animation constants
    const line1 = 'Hello! I am MUKALMA, An Intelligent Q/A' 
    const line2 = 'Chatbot'

    const sentence = {
        hidden: { opacity: 1 },
        visible: {
            opacity: 1,
            transition: {
                delay: 0.5,
                staggerChildren: 0.05,
            },
        },
    }
    const letter = {
        hidden: { opacity: 0, y: 50 },
        visible: {
            opacity: 1,
            y: 0,
        },
    }

    // Building Layout
    return (
        <div className='splash-container'>
                <div className='splash-div'>
                    <motion.div
                        animate={{ x: [0, -565], y: [0, -135], scale: [1, 0.225]}}
                        transition={{ delay: 3.3 }}
                    >
                        <motion.div
                            animate={{ scale: [0, 1], opacity: [0, 1] }}
                        >
                        <img 
                            src={images.splashLogo}
                            className="splash-screen-logo"
                        />
                        </motion.div>
                    </motion.div>
                    <br />
                    <motion.div
                        animate={{ x: [0, -410], y: [0, -225],scale: [1, 0.85]}}
                        transition={{ delay: 3.3 }}
                    >
                        <motion.h5
                            variants={sentence}
                            initial="hidden"
                            animate="visible"
                            transition={{ delay: 1 }}
                        >
                            {line1.split("").map((char, index) => (
                                <motion.span key={`${char}-${index}`} variants={letter}>
                                    {char}
                                </motion.span>
                            ))}
                            <br />
                            {line2.split("").map((char, index) => (
                                <motion.span key={`${char}-${index}`} variants={letter}>
                                    {char}
                                </motion.span>
                            ))}
                        </motion.h5>
                    </motion.div>
                </div>
        </div>
    )
}

export default SplashScreen
