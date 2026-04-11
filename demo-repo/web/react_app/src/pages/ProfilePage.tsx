import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../services/apiClient';
import { Loader } from '../components/Loader';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  createdAt: string;
}

/**
 * User profile page
 * Calls: GET /auth/me
 * Requires: JWT authentication
 */
export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/auth/me');
      setProfile(response.data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <Loader />;
  }

  return (
    <div className="profile-page">
      <h1>My Profile</h1>
      {profile && (
        <div className="profile-card">
          {profile.avatarUrl && (
            <img src={profile.avatarUrl} alt={profile.name} />
          )}
          <h2>{profile.name}</h2>
          <p>{profile.email}</p>
          <p>Member since: {new Date(profile.createdAt).toLocaleDateString()}</p>
        </div>
      )}
    </div>
  );
};
