import React from 'react'
import './ResponseProgress.css'

import { Stepper, Step, StepButton, Chip, CircularProgress } from '@material-ui/core'

const ResponseProgress = ({ responseProgressMessage, activeStep }) => {

    // Steps
    const steps = [0, 1, 2, 3]
    
    // Building Layout
    return (
        <div className={"progress-container"}>
            <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((id) => (
                    <Step key={id} >
                        <StepButton color="inherit"/>
                    </Step>
                ))}
            </Stepper>
            <CircularProgress className={"status-circle"} size={20}/>
            <Chip 
                label={responseProgressMessage}  
                className={"status-chip"}  
                variant="outlined"
                color="primary" 
                size='medium'       
            />
        </div>
    )
}

export default ResponseProgress
