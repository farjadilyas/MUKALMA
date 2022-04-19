import React, { useState } from "react";
import { AppBar, Typography, IconButton, TextField } from "@material-ui/core";
import { Link } from '@material-ui/icons'

import useStyles from './styles'
import { motion } from 'framer-motion'
import { values } from '../../constants'

const Navbar = () => {

    // Using a variable for displaying the URL input field
    const [showInputField, setShowInputField] = useState(false);

    // Using JS-style CSS for this component
    const classes = useStyles();

    // Function to toggle inputField
    const toggleURLInputField = () => {
        setShowInputField(!showInputField);
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
                        <motion.div animate={{ x: [-30, 0], opacity: [0, 1] }}>
                            <TextField label="URL"/>
                        </motion.div>
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
