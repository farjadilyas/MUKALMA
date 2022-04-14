import * as React from 'react';

import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';

import Source from '../Source/Source'
import Topic from '../Topic/Topic'
import Responses from '../Responses/Responses'
import InformationRetrieval from '../InformationRetrieval/InformationRetrieval';

import './Tabs.css'
import { IconButton } from '@mui/material';
import { Close } from '@material-ui/icons' 

const TabContainer = ({ 
        source, 
        setSource, 
        spanSelected, 
        topic, 
        setTopic, 
        topics, 
        setTopics, 
        setMessages, 
        responses,
        selectedTopic, 
        value,
        setValue
    }) => {
    
    // Selecting and Changing value
    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    // Removing the bar function
    const hideTab = (event, newValue) => {
        setValue(-1);
    }

    const labels = ["Knowledge Source", "Candidate Responses", "Topic Selection", "Information Retrieval"]

    // Function to dynamically select the component to render based on the value of the tab
    // container
    const componentSelect = (value) => {
        switch(value) {
            case 0:
                return <Source 
                    source={source} 
                    setSource={setSource} 
                    spanSelected={spanSelected}
                />
            case 1:
                return <Responses responses={responses}/>
            case 2:
                return <Topic 
                        topic={topic} 
                        setTopic={setTopic} 
                        topics={topics} 
                        setTopics={setTopics} 
                        setSource={setSource}
                        setMessages={setMessages} 
                    />
            case 3:
                return <InformationRetrieval selectedTopic={selectedTopic}/>
            default:
                return <></>
        }
    }

    // Building Layout
    return (
        <Box sx={{ bgcolor: 'background.paper' }} className={"box"}>
            { value < 0 ?
                <Tabs
                    value={value}
                    onChange={handleChange}
                    scrollButtons={false}
                    aria-label="scrollable prevent tabs example"
                    orientation="vertical"
                >
                    {
                        labels.map((lb, index) => (
                        <Tab label={lb} wrapped/>
                        ))
                    }
                </Tabs>
                :
                <></>
            }
            { value >= 0 ?
                <Box className={"box"}>
                    <div className={"tab-bar"}>
                        <h6>{labels[value]}</h6>
                        <div />
                        <IconButton onClick={hideTab}>
                            <Close />
                        </IconButton>
                    </div>
                    {componentSelect(value)}
                </Box>
                :
                <></>
            }
        </Box>
    );
}

export default TabContainer
