import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { AppStateProvider } from "./_state-controller/state-controller";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <AppStateProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
        </Stack>
      </AppStateProvider>
    </SafeAreaProvider>
  );
}
