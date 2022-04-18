import * as React from 'react';

import { Tabs, Tab, Box } from '@mui/material'

import { Source, Topics, InformationRetrieval, Responses } from '../../components'

import './TabContainer.css'
import { IconButton } from '@mui/material';
import { Close } from '@material-ui/icons' 

const TabContainer = ({ 
        source, 
        setSource, 
        spanSelected, 
        topics, 
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

    const labels = ["Knowledge Source", "Candidate Responses", "Topic Transitions", "Information Retrieval"]

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
                return <Topics topics={topics}/>
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
                    {labels.map((lb) => (
                        <Tab 
                            label={lb} 
                            wrapped
                            className={"tab-hover"}
                        />
                    ))}
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
