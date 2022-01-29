
import List from '@material-ui/core/List';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';
import { makeStyles } from '@material-ui/core/styles';

import ProgressBar from './ProgressBar';

const useStyles = makeStyles(() => ({
    squeeze: { paddingTop: 0, paddingBottom: 0, marginTop: 0, marginBottom: 0 },
}));

export default function AutoPostResult(props) {
    const classes = useStyles();
    return (
        <Paper>
            <Box m={2}>
                <List>
                    <div>Auto Posting:</div>
                    {(props.progress >=0 && props.progress <=100) ? <ProgressBar value={props.progress} /> : <Divider />}
                    {props.posts.map(p =>
                        <ListItemText classes={{ root: classes.squeeze }} disableTypography key={p.id} primary={`${p.msg}`} />
                    )}
                </List>
            </Box>
        </Paper>
    )
}