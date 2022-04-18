import React, { useState, useEffect } from "react";

import { Grid } from "@material-ui/core";
import { motion } from 'framer-motion';

import { Chatbox, TabContainer } from '../../components';
import Speech from './Speech/Speech';

import { initialState } from "../Chatbox/state";

import './Home.css';

import { values } from '../../constants'

const Home = () => {

    // Messages
    const [messages, setMessages] = useState(initialState)

    // Responses
    const [responses, setResponses] = useState(["Response 1", "Response 2"])

    // Tabs
    const [value, setValue] = React.useState(-1);

    // Topic
    const [topics, setTopics] = useState([{ 
        "knowledge_article": "Multan", 
        "keywords": ["multan", "city", "pakistan"] 
    }]);
    const [spanSelected, setSpanSelected] = useState(/Fusce placerat consequat elementum./g)
    const [selectedTopic, setSelectedTopic] = useState('Multan')

    // Speech
    const [speechText, setSpeechText] = useState(values.GREETING);
    const [playAudio, setPlayAudio] = useState(true);

    // Source
    const [source, setSource] = useState(values.DUMMY_SOURCE);

    // Using Effect to start voice if the Speech Text changes
    useEffect(() => {
        setPlayAudio(true);
    }, [speechText]);

    // Building HTML
    return (
        <div className={"mainContainer"} >
            <Grid container spacing={2} className={"gridContainer"} >
                { value < 0 ?
                    <Grid item xs={12} sm={1} className={"gridItem"} />
                    : <></>
                }
                <Grid item xs={12} sm={ value < 0 ? 10 : 6 } className={"gridItem"} >
                    <Chatbox 
                        messages={messages} 
                        setMessages={setMessages} 
                        setSource={setSource}
                        setSpanSelected={setSpanSelected}
                        setResponses={setResponses}
                        setSpeechText={setSpeechText}
                        setTopics={setTopics}
                    />
                </Grid>
                <Grid item xs={12} sm={ value < 0 ? 1 : 6 } className={"gridItem"} >
                    <motion.div
                        animate={{ x: [30, 0], opacity: [0, 1] }}
                        style={{ height: "93%" }}
                    >
                        <TabContainer 
                            source={source} 
                            setSource={setSource} 
                            spanSelected={spanSelected}
                            topics={topics}
                            setTopics={setTopics}
                            setMessages={setMessages}
                            responses={responses}
                            selectedTopic={selectedTopic}
                            value={value}
                            setValue={setValue} 
                        />
                    </motion.div>
                </Grid>
            </Grid>
            <div style={{ visibility: "hidden" }}>
                <Speech
                    text={speechText}
                    voice={values.VOICE}
                    play_audio={playAudio}
                    setPlayAudio={setPlayAudio}
                />
            </div>
        </div>
    );
}

export default Home;
