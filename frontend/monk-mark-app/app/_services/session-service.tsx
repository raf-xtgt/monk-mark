


import { UserService } from './user-service';
import { UserStateDto } from '../_model/dto/user-state-dto';
import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
    USER_GUID: 'UserStateDto.guid',
    USER_NAME: 'UserStateDto.userName',
    USER_EMAIL: 'UserStateDto.email',
};

export const SessionService = {
    async getOrCreateUser(payload: { email: string }): Promise<UserStateDto> {
        try {
            // Check AsyncStorage for existing user
            const storedGuid = await AsyncStorage.getItem(STORAGE_KEYS.USER_GUID);
            const storedUserName = await AsyncStorage.getItem(STORAGE_KEYS.USER_NAME);
            const storedEmail = await AsyncStorage.getItem(STORAGE_KEYS.USER_EMAIL);

            if (storedGuid && storedUserName && storedEmail) {
                // User exists in AsyncStorage
                const userState: UserStateDto = {
                    guid: storedGuid,
                    userName: storedUserName,
                    email: storedEmail,
                };
                return userState;
            }

            // User doesn't exist, create new one
            const createdUser = await UserService.autoCreateDefaultUser({
                email: payload.email,
            });

            // Generate userName from guid
            const userName = `test-user-${createdUser.guid.substring(0, 5)}`;

            const userState: UserStateDto = {
                guid: createdUser.guid,
                userName: userName,
                email: createdUser.email,
            };

            // Store in AsyncStorage
            await AsyncStorage.setItem(STORAGE_KEYS.USER_GUID, userState.guid);
            await AsyncStorage.setItem(STORAGE_KEYS.USER_NAME, userState.userName);
            await AsyncStorage.setItem(STORAGE_KEYS.USER_EMAIL, userState.email);

            return userState;
        } catch (error) {
            console.error('Error in getOrCreateUser:', error);
            throw error;
        }
    },
};


