import { AppBar, Typography } from "@material-ui/core";
import useStyles from './styles'
import { motion } from 'framer-motion'
import { values } from '../../constants'

const Navbar = () => {
    
    const classes = useStyles();

    // Building HTML
    return (
        <AppBar className={classes.appBar} position='absolute' color="inherit">
            <div className={classes.left}>
                <motion.div
                    animate={{ x: [-30, 0], opacity: [0, 1] }}
                >
                    <Typography className={classes.heading} variant="h2" align="center">
                        {values.MUKALMA}
                    </Typography>
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
