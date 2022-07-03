import React, { useState } from "react";
import { useDispatch } from 'react-redux';

import { AppBar, Typography, IconButton, TextField, Button } from "@material-ui/core";
import { Link } from '@material-ui/icons'

import useStyles from './styles'
import { motion } from 'framer-motion'
import { values } from '../../constants'

import { updateApiUrl } from "../../api";
import { connectToApi } from '../../actions/message';

const Navbar = ({ asyncApi, setAsyncApi }) => {

    // Using a variable for displaying the URL input field
    const [showInputField, setShowInputField] = useState(false);
    const [url, setUrl] = useState('');
    const [connectionStatus, setConnectionStatus] = useState(false);

    // Using JS-style CSS for this component
    const classes = useStyles();

    // Dispatcher
    const dispatch = useDispatch();

    // Function to toggle inputField
    const toggleURLInputField = () => {
        setShowInputField(!showInputField);
    }

    const toggleAsyncApi = () => {
        setAsyncApi(!asyncApi);
    }

    // Function to update API url
    const handleSubmit = (event) => {
        if (event) {
            event.preventDefault();
        }
        updateApiUrl(url);
        setShowInputField(false);
        setUrl('');
        dispatch(
            connectToApi(setConnectionStatus)
        );
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
                    {
                        connectionStatus ? 
                        <Typography variant="body2" color="primary">
                            CONNECTED
                        </Typography> 
                        : <></>
                    }
                    <Button onClick={toggleAsyncApi} color={ asyncApi ? "primary" : "secondary" }>
                        { asyncApi ? "ASYNC" : "SYNC" }
                    </Button>
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
