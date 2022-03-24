import { deepPurple } from '@material-ui/core/colors';
import { makeStyles } from '@material-ui/core/styles'

export default makeStyles((theme) => ({
    appBar: {
        margin: '0',
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 50px',
        [theme.breakpoints.up('sm')]: {
            flexDirection: 'row',
        },
    },
    heading: {
        color: 'rgba(0, 183, 255, 1)',
        textDecoration: 'none',
        userSelect: 'none',
        display: 'flex',
    },
    image: {
        marginLeft: '15px',
    },
    toolbar: {
        display: 'flex',
        justifyContent: 'flex-end',
        width: '400px',
    },
    profile: {
        display: 'flex',
        justifyContent: 'space-between',
        width: '400px'
    },
    userName: {
        display: 'flex',
        alignItems: 'center',
    },
    brandContainer: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    purple: {
        color: theme.palette.getContrastText(deepPurple[500]),
        backgroundColor: deepPurple[500],
    },
    Members: {
        textAlign: 'right',
        whiteSpace: 'pre-line',
        marginRight: '10px',
        margin: '0',
        position: 'relative',
        userSelect: 'none',
        display: 'flex',
    }, 
    grow: {
        flexGrow: 1,
    },
    left: {
        flexGrow: 1,
        display: 'flex',
    },
    right: {
        display: 'flex',
    },
}));
