import React from 'react';
import { useSelector } from 'react-redux'

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Avatar from '@material-ui/core/Avatar';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import { red } from '@material-ui/core/colors';

import { selectAllUsers } from '../user/userSlice';

const useStyles = makeStyles((theme) => ({
    root: {
        display: "inline-block"
    },
    avatar: {
        backgroundColor: red[500],
    },
}));

export function Users() {
    const users = useSelector(selectAllUsers);
    return (
        <>
            <Grid container spacing={2}>
                {users.map(u =>
                    <Grid item key={u.id}>
                        <User {...u} />
                    </Grid>
                )}
            </Grid>
        </>
    );
}

export function User(props) {
    const classes = useStyles();
    return (
        <Card className={classes.root}>
            <CardHeader
                avatar={<Avatar aria-label="recipe" className={classes.avatar} children={props.id[0].toUpperCase()} />}
                title={props.id}
                subheader="September 14, 2016"
            />
            <CardContent>
                <Typography variant="body2" color="textSecondary" component="p">
                    password: {props.password}
                </Typography>
                <Typography variant="body2" color="textSecondary" component="p">
                    email: {props.email}
                </Typography>
                <Typography variant="body2" color="textSecondary" component="p">
                    posts: {props.posts}
                </Typography>
                <Typography variant="body2" color="textSecondary" component="p">
                    coins: {props.coins}
                </Typography>
                <Typography variant="body2" color="textSecondary" component="p">
                    contributions: {props.contributions}
                </Typography>
            </CardContent>
            <CardActions>
                <Button size="small" href={`autopost/${props.id}`}>Auto Post</Button>
            </CardActions>
        </Card>
    );
}