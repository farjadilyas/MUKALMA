import './Topic.css'
import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import CircularProgress from '@mui/material/CircularProgress';
import { topicSelect } from '../../actions/message';
import SearchBar from "material-ui-search-bar";
import Chip from '@mui/material/Chip';
import { Grid } from "@material-ui/core";

const Topic = ({ topic, setTopic, topics, setTopics, setSource, setMessages }) => {
    // Dispatcher
    const dispatch = useDispatch()

    // Handling Change
    const handleChange = (event) => {
        setTopic(topic => event.target.value)
        dispatch(topicSelect(event.target.value, setSource, setMessages));
    };

    // Search Bar
    const [search, setSearch] = useState("")

    // Progress Bar Visibility
    const [progress, setProgress] = useState("hidden")

    const onSearch = () => {
        dispatch(topicSelect(search, setSource, setMessages, setProgress));
        setProgress("visible")
    }

    // Building HTML
    return (
        <div className="container">
          <div className='inputGroup'>
            <InputLabel>
              Current Topic Tags
            </InputLabel>
            <Grid container spacing={1}>
              {['Multan', 'Multan Qalanders', 'Punjab', 'Chenab River'].map((tag, index) => (
                <Grid item xs={12} sm={6} md={4}>
                  <Chip label={tag} variant="outlined" />
                </Grid>
              ))}
            </Grid>
          </div>
          <div className='inputGroup'>
            <InputLabel id="topicSelect">
              Select a topic of conversation from our collection
            </InputLabel>
            <Select
              labelId="topicSelect"
              id="demo-simple-select-helper"
              value={topic}
              label="Topic"
              onChange={handleChange}
              className="selector"
            >
              {topics.map(topic => {
                  return topic !== "Custom" ? <MenuItem value={topic}>{topic}</MenuItem> : null
              })}
            </Select>
          </div>
          <div className='inputGroup'>
            <InputLabel 
              id="topicSearch" 
              className="inputLabel">
                Or search for any topic
            </InputLabel>
            <SearchBar 
              value={search} 
              className="searchBar" 
              onChange={(newValue) => setSearch(newValue)} onRequestSearch={onSearch}/>
            <CircularProgress className="progress" style={{ visibility: progress }}/>
          </div>
      </div>
    )
}

export default Topic
