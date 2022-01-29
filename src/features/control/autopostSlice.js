import { createSlice } from '@reduxjs/toolkit';
import { createEntityAdapter } from '@reduxjs/toolkit'
import { createAsyncThunk } from '@reduxjs/toolkit'

export const autopost = createAsyncThunk('autopost/trigger', async (userData) => {
    let data = {
        method: "POST",
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: JSON.stringify(userData)
    }
    const result = await fetch("http://localhost:6001/autopost", data).then(res => res.json())
    return result
})

export const fetchAutoPostResults = createAsyncThunk('autopost/fetch', async (userData) => {
    const result = await fetch(`http://localhost:6001/autopost?userId=${userData.userId}&currentId=${userData.currentId}`).then(res => res.json())
    return result
})

const adapter = createEntityAdapter({
    sortComparer: (a, b) => b.id === a.id
})
const initialState = adapter.getInitialState({ progress: -1, errorMsg: ""})

export const autopostSlice = createSlice({
    name: 'autopost',
    initialState,
    reducers: {
        clearResult: (state) => {
            state.progress = 0
            state.errorMsg = ""
            adapter.removeAll(state)
        }
    },
    extraReducers: (builder) => {
        builder.addCase(fetchAutoPostResults.fulfilled, (state, action) => {
            if ("progress" in action.payload)
                state.progress = action.payload.progress
            if ("posts" in action.payload)
                adapter.addMany(state, action.payload.posts)
        })
        .addCase(fetchAutoPostResults.rejected, (state) => {
            state.errorMsg = "Error in getting autopost results"
        })
    },
});

export const {
    selectAll: selectAllPosts,
    selectById: selectPostById,
    selectIds: selectPostIds
} = adapter.getSelectors(state => state.autopost)

export const selectProgress = state => state.autopost.progress;
export const selectBiggestId = state => (state.autopost.ids.length > 0) ? state.autopost.ids.reduce((preId, curId)=>{return (preId > curId ? preId : curId)}) : -1

export const { clearResult } = autopostSlice.actions;

export default autopostSlice.reducer;