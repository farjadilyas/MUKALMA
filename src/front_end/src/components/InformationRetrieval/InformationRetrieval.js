import React from 'react'
import { Grid, InputLabel, Chip } from '@mui/material'

import { HighlightWithinTextarea } from 'react-highlight-within-textarea'
import { CircularProgressWithLabel } from './CircularProgressWithLabel/CircularProgressWithLabel'

import './styles.css'

const InformationRetrieval = ({ selectedTopic }) => {

    // Building and returning layout
    return (
        <div class="container">
            <div>
                <InputLabel className='topic-tags-title'>
                    Current Topic Tags
                </InputLabel>
                <Grid container spacing={1}>
                    {['Multan', 'Multan Qalanders', 'Punjab', 'Chenab River'].map((tag, index) => (
                        <Grid item xs={12} sm={6} md={4}>
                            <Chip 
                                label={tag} 
                                variant={tag === selectedTopic ? "" : "outlined" } 
                                color="primary"
                                component="a"
                                clickable
                                href=""
                                style={{ textDecoration: 'none' }}/>
                        </Grid>
                    ))}
                </Grid>
            </div>
            <div style={{ alignItems: "center" }}>
                <InputLabel className='topic-tags-title'>
                    Noun Selection
                </InputLabel>
                <HighlightWithinTextarea 
                    value="Hey, have you been to Multan?" 
                    highlight="Multan" 
                />
            </div>
            <div className='matched-container'>
                <InputLabel className='topic-tags-title'>
                    Percentage Matched
                </InputLabel>
                <CircularProgressWithLabel value={34} size={130}/>
            </div>
        </div>
    )
}

export default InformationRetrieval
