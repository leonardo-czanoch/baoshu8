import { configureStore } from '@reduxjs/toolkit';
import counterReducer from '../features/counter/counterSlice';
import userReducer from '../features/user/userSlice';
import autopostReducer from '../features/control/autopostSlice';

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    user: userReducer,
    autopost: autopostReducer,
  },
});
