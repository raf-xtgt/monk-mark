import React from 'react';
import HomeContainer from './pages/home/home-container';
import LibraryContainer from './pages/library/library-container';
import NotebookContainer from './pages/notebook/notebook-container';
import MonkModeContainer from './pages/monk-mode/monk-mode-container';
import ProfileContainer from './pages/profile/profile-container';
import NoteTakerContainer from './pages/notebook/note-taker-container';

export const routes = [
  { id: 1, name: 'Home', component: HomeContainer, path: '/' },
  { id: 2, name: 'Library', component: LibraryContainer, path: '/library' },
  { id: 3, name: 'Notebook', component: NotebookContainer, path: '/notebook' },
  { id: 4, name: 'MonkMode', component: MonkModeContainer, path: '/monk-mode' },
  { id: 5, name: 'Profile', component: ProfileContainer, path: '/profile' },
  { id: 6, name: 'NoteTaker', component: NoteTakerContainer, path: '/note-taker' },
];

interface RouterProps {
  currentRoute: number;
}

const Router: React.FC<RouterProps> = ({ currentRoute }) => {
  const route = routes.find(r => r.id === currentRoute);
  
  if (!route) {
    return <HomeContainer />;
  }

  const Component = route.component;
  return <Component />;
};

export default Router;
