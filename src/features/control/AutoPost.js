import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux'
import { useParams } from "react-router-dom";

import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Snackbar from '@material-ui/core/Snackbar';

import AutoPostFrom from './AutoPostForm';
import AutoPostResult from './AutoPostResult';

import { selectAllPosts, selectProgress, selectBiggestId } from './autopostSlice';
import { fetchAutoPostResults } from '../control/autopostSlice';

export function AutoPost() {
    let { userId } = useParams();

    const [timer, setTimer] = useState(null)
    const [open, setOpen] = useState(false)

    const dispatch = useDispatch();

    const posts = useSelector(selectAllPosts);
    const progress = useSelector(selectProgress);
    const latestPostId = useSelector(selectBiggestId);
    const errorMsg = useSelector(state=>state.autopost.errorMsg)

    useEffect(() => {
        if (timer) {
            clearInterval(timer)
        }
        const newTimer = setInterval(() => { dispatch(fetchAutoPostResults({ userId: userId, currentId: latestPostId })) }, 5000)
        setTimer(newTimer)
    }, [userId, latestPostId])

    useEffect(()=>{
        setOpen(errorMsg ? true : false)
    }, [errorMsg])

    return (
        <>
            <Grid container alignItems="flex-start">
                <Grid item>
                    <AutoPostFrom userId={userId} isAutoPosting={progress >= 0 && progress < 100} />
                </Grid>
                <Grid item xs>
                    <AutoPostResult posts={posts} progress={progress} />
                </Grid>
            </Grid>

            <Snackbar
                anchorOrigin={{ vertical: "top", horizontal: "center" }}
                open={open} autoHideDuration={5000} onClose={()=>setOpen(false)}
                message={errorMsg}
                key={"errorMsg"}
            />
        </>
    );
}