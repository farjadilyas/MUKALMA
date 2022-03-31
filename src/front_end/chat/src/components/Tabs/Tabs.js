import * as React from 'react';

import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';

import Source from '../Source/Source'
import Topic from '../Topic/Topic'
import Responses from '../Responses/Responses'
import InformationRetrieval from '../InformationRetrieval/InformationRetrieval';

import './Tabs.css'

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
}) => {
  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const componentSelect = (value) => {
      switch(value) {
          case 0:
              return <Source source={source} setSource={setSource} spanSelected={spanSelected}/>
          case 1:
              return <Responses responses={responses}/>
          case 2:
              return <Topic 
              topic={topic} 
              setTopic={setTopic} 
              topics={topics} 
              setTopics={setTopics} 
              setSource={setSource}
              setMessages={setMessages}/>
          case 3:
              return <InformationRetrieval selectedTopic={selectedTopic}/>
          default:
              return <h1></h1>
      }
  }

  return (
    <Box sx={{ maxWidth: 620, bgcolor: 'background.paper' }}>
      <Tabs
        value={value}
        onChange={handleChange}
        variant="scrollable"
        scrollButtons={false}
        aria-label="scrollable prevent tabs example">
          {["Knowledge Source", "Candidate Responses", "Topic Selection", "Information Retrieval"].map((lb, index) => (
            <Tab label={lb} wrapped/>
          ))}
      </Tabs>
      <Box sx={{ maxWidth: 620, minHeight: 450 }}>
            {componentSelect(value)}
      </Box>
    </Box>
  );
}

export default TabContainer
