import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";

import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import Link from '@material-ui/core/Link';
import MenuIcon from '@material-ui/icons/Menu';
import { makeStyles } from '@material-ui/core/styles';

import Box from '@material-ui/core/Box';

import { AutoPost } from './features/control/AutoPost';
import { Users } from './features/user/User';

const useStyles = makeStyles(() => ({
  title: { flexGrow: 1 },
}));

function App() {
  const [drawer, setDrawer] = useState(false)
  const classes = useStyles();

  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu" onClick={() => { setDrawer(true) }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" className={classes.title}>
            Baoshu8
          </Typography>
          <Button color="inherit">Login</Button>
        </Toolbar>
      </AppBar>
      <Box component="span" m={1}>
        <Router>
          <Switch>
            <Route path="/autopost/:userId" component={AutoPost} />
            <Route path="/autopost" component={AutoPost} />
            <Route path="/" component={Users} />
          </Switch>
        </Router>
        <Drawer anchor={"left"} open={drawer}>
          <List>
            <ListItem button key="users" onClick={() => { setDrawer(false) }}>
              <Link href="/" onClick={() => { setDrawer(false) }} variant="body2">
              users
              </Link>
            </ListItem>
            <ListItem button key="autopost">
              <Link href="/autopost" onClick={() => { setDrawer(false) }} variant="body2">
              autopost
              </Link>
            </ListItem>
          </List>
        </Drawer>
      </Box>
    </div>
  );
}

export default App;
