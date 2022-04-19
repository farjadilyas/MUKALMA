import React from 'react'

import { VerticalTimeline, VerticalTimelineElement } from 'react-vertical-timeline-component';
import 'react-vertical-timeline-component/style.min.css';

import './Topics.css'

const Topics = ({ topics }) => {
    // Building HTML
    return (
        <div className="container">
            <VerticalTimeline className='timeline-container' lineColor='gainsboro'>
                {topics.map((topic, index) => (
                    <VerticalTimelineElement
                        contentStyle={{ background: '#f1f0f0', color: '#212529', padding: '15px'}}
                        contentArrowStyle={{ borderRight: '7px solid #f1f0f0' }}
                        iconStyle={{ background: '#2285ff', color: 'white' }}
                    >
                        <h5 className="vertical-timeline-element-title">{topic.knowledge_article}</h5>
                        <div className='tags-container'>
                            {topic.keywords.map((keyword, index) => (
                                <p style={{ fontSize: 'medium', margin: '2px', fontWeight: 'normal'}}>
                                    #{keyword}
                                </p>
                            ))}
                        </div>
                    </VerticalTimelineElement>
                ))}
            </VerticalTimeline>
        </div>
    )
}

export default Topics
