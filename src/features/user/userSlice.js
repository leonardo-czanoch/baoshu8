import { createSlice } from '@reduxjs/toolkit';
import { createEntityAdapter } from '@reduxjs/toolkit'
import { createAsyncThunk } from '@reduxjs/toolkit'

export const fetchUsers = createAsyncThunk('user/fetch', async () => {
    const users = await fetch("http://localhost:6001/user").then(res => res.json())
    return users
})

const adapter = createEntityAdapter({
    sortComparer: (a, b) => b.id.localeCompare(a.id)
})
const initialState = adapter.getInitialState()

export const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {},
    extraReducers: {
        [fetchUsers.fulfilled]: adapter.addMany,
    },
});

export const {
    selectAll: selectAllUsers,
    selectById: selectUserById,
    selectIds: selectUserIds
} = adapter.getSelectors(state => state.user)

export const { populate } = userSlice.actions;

export default userSlice.reducer;