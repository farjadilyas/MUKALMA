import React, { useState } from "react";
import { AppBar, Typography, IconButton, TextField } from "@material-ui/core";
import { Link } from '@material-ui/icons'

import useStyles from './styles'
import { motion } from 'framer-motion'
import { values } from '../../constants'

import { updateApiUrl } from "../../api";

const Navbar = () => {

    // Using a variable for displaying the URL input field
    const [showInputField, setShowInputField] = useState(false);
    const [url, setUrl] = useState('');

    // Using JS-style CSS for this component
    const classes = useStyles();

    // Function to toggle inputField
    const toggleURLInputField = () => {
        setShowInputField(!showInputField);
    }

    // Function to update API url
    const handleSubmit = (event) => {
        if (event) {
            event.preventDefault();
        }
        updateApiUrl(url);
        setShowInputField(false);
        setUrl('')
    }

    // Building HTML
    return (
        <AppBar className={classes.appBar} position='absolute' color="inherit">
            <div className={classes.left}>
                <motion.div
                    animate={{ x: [-30, 0], opacity: [0, 1] }}
                    className={classes.titleContainer}
                >
                    <Typography className={classes.heading} variant="h2" align="center">
                        {values.MUKALMA}
                    </Typography>
                    <IconButton onClick={toggleURLInputField}>
                        <Link />
                    </IconButton>
                    { showInputField ?
                        <form onSubmit={handleSubmit}>
                            <TextField 
                                label="URL" 
                                value={url} 
                                onChange={(event) => setUrl(event.target.value)}
                                fullWidth={true}
                            />
                        </form>
                        :
                        <></>
                    }
                </motion.div>
            </div>
            <div className={classes.grow}/>
            <div className={classes.right}>
                <motion.div
                    animate={{ x: [30, 0], opacity: [0, 1] }}
                >
                    <Typography variant="overline" display="block" gutterBottom className={classes.Members}>
                        {values.MEMBERS}
                    </Typography>
                </motion.div>
            </div>
        </AppBar>
    )
}

export default Navbar
