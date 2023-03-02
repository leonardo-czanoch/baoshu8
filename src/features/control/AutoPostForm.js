import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux'

import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import MenuItem from '@material-ui/core/MenuItem';
import Switch from '@material-ui/core/Switch';
import FormGroup from '@material-ui/core/FormGroup';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormLabel from '@material-ui/core/FormLabel';
import Radio from '@material-ui/core/Radio';
import Input from '@material-ui/core/Input';
import RadioGroup from '@material-ui/core/RadioGroup';
import Box from '@material-ui/core/Box';

import { selectAllUsers } from '../user/userSlice';
import { autopost } from '../control/autopostSlice';
import { clearResult } from '../control/autopostSlice';

export default function AutoPostForm(props) {
    const [userId, setUserId] = useState(props.userId);
    const [numOfPost, setNumOfPost] = useState(50);
    const [checkin, setCheckin] = useState(true);
    const [sections, setSections] = useState({ baidupan_movie: false, baidupan_series: false, baidupan_comic: false, baidupan_documentary: false, baidupan_classic: true });
    const [algorithm, setAlgorithm] = useState("absolutelyRandom");

    const dispatch = useDispatch();
    const users = useSelector(selectAllUsers);

    const earnPoints = ()=>{
        dispatch(clearResult())
        dispatch(autopost({userId, numOfPost, checkin, sections, algorithm}))
    }

    return (
        <>
            <Box m={2}>
                <FormLabel component="legend">User</FormLabel>
                <Select value={userId} onChange={(event) => setUserId(event.target.value)} disabled={props.isAutoPosting}>
                    <MenuItem key="None" value=""><em>None</em></MenuItem>
                    {users && users.map(u => <MenuItem key={u.id} value={u.id}>{u.id}</MenuItem>)}
                </Select>

                <FormLabel component="legend">Number of Posting</FormLabel>
                <Input value={numOfPost} disabled={props.isAutoPosting}
                    onChange={event => setNumOfPost(event.target.value === '' ? '' : Number(event.target.value))}
                    onBlur={() => setNumOfPost(numOfPost < 0 ? 0 : (numOfPost > 100 ? 100 : numOfPost))}
                    inputProps={{ step: 1, min: 1, max: 50, type: 'number' }}
                />

                <FormLabel component="legend">Sections</FormLabel>
                <FormGroup>
                    {Object.keys(sections).map(s =>
                        <FormControlLabel disabled={props.isAutoPosting}
                            control={<Checkbox checked={sections[s]} onChange={(e) => setSections({ ...sections, [s]: e.target.checked })} />}
                            key={s} label={s}
                        />
                    )}
                </FormGroup>

                <FormLabel component="legend">Section Choosing Algorithm</FormLabel>
                <RadioGroup aria-label="Algorithm" value={algorithm} onChange={(event) => setAlgorithm(event.target.value)}>
                    <FormControlLabel value="absolutelyRandom" control={<Radio />} label="Absolutely Random" disabled={props.isAutoPosting} />
                    <FormControlLabel value="evenlyRandom" control={<Radio />} label="Evenly Random" disabled={props.isAutoPosting} />
                </RadioGroup>

                <FormLabel component="legend">Simultaneous Actions</FormLabel>
                <FormControlLabel disabled={props.isAutoPosting}
                    control={
                        <Switch checked={checkin} onChange={(event) => setCheckin(event.target.checked)} color="primary" />
                    }
                    label="Check-In"
                />
            </Box>
            <Box m={2}>
                <Button variant="contained" m={2} color="primary" children="AutoPost" onClick={earnPoints} />
            </Box >
        </>
    );
}