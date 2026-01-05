import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
  Divider,
  Switch,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Avatar,
  Card,
  CardContent,
  Grid,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormGroup,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import {
  Person as PersonIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  Palette as PaletteIcon,
  Group as GroupIcon,
  CreditCard as PaymentIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  AutoAwesome as AutoIcon,
  Backup as BackupIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/api';
import { User, UserProfile } from '../types';

const Settings: React.FC = () => {
  const { user, logout } = useAuth();
  const [selectedTab, setSelectedTab] = useState(0);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [openProfileDialog, setOpenProfileDialog] = useState(false);
  const [openPasswordDialog, setOpenPasswordDialog] = useState(false);
  const [profileData, setProfileData] = useState({
    display_name: '',
    dietary_tags: [] as string[],
    allergens: [] as string[],
    preferences: {}
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [settings, setSettings] = useState({
    notifications: true,
    email_notifications: true,
    push_notifications: false,
    dark_mode: false,
    ai_suggestions: true,
    data_sharing: false,
    auto_backup: true
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const profile = await userService.getProfile();
      setUserProfile(profile);
      setProfileData({
        display_name: profile.display_name || '',
        dietary_tags: profile.dietary_tags || [],
        allergens: profile.allergens || [],
        preferences: profile.preferences || {}
      });
    } catch (err) {
      console.error('Error loading profile:', err);
    }
  };

  const handleSaveProfile = async () => {
    try {
      const updatedProfile = await userService.updateProfile(profileData);
      setUserProfile(updatedProfile);
      setOpenProfileDialog(false);
      setSnackbar({
        open: true,
        message: 'Profile updated successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to update profile',
        severity: 'error'
      });
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setSnackbar({
        open: true,
        message: 'Passwords do not match',
        severity: 'error'
      });
      return;
    }

    try {
      await userService.changePassword(passwordData);
      setOpenPasswordDialog(false);
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setSnackbar({
        open: true,
        message: 'Password changed successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to change password',
        severity: 'error'
      });
    }
  };

  const handleExportData = () => {
    // In a real app, this would trigger a data export
    setSnackbar({
      open: true,
      message: 'Data export started. You will receive an email when ready.',
      severity: 'info'
    });
  };

  const handleDeleteAccount = () => {
    // In a real app, this would show a confirmation and then delete the account
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      console.log('Deleting account...');
      logout();
    }
  };

  const dietaryOptions = [
    'vegetarian', 'vegan', 'keto', 'paleo', 'gluten-free', 'dairy-free', 'low-carb', 'high-protein'
  ];

  const allergenOptions = [
    'nuts', 'dairy', 'eggs', 'fish', 'shellfish', 'soy', 'wheat', 'sesame'
  ];

  const menuItems = [
    { text: 'Profile', icon: <PersonIcon />, action: () => setSelectedTab(0) },
    { text: 'Account Security', icon: <SecurityIcon />, action: () => setSelectedTab(1) },
    { text: 'Notifications', icon: <NotificationsIcon />, action: () => setSelectedTab(2) },
    { text: 'Preferences', icon: <PaletteIcon />, action: () => setSelectedTab(3) },
    { text: 'Household', icon: <GroupIcon />, action: () => setSelectedTab(4) },
    { text: 'Billing & Plans', icon: <PaymentIcon />, action: () => setSelectedTab(5) },
    { text: 'Data & Privacy', icon: <StorageIcon />, action: () => setSelectedTab(6) }
  ];

  const renderProfileSection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Profile Settings
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={3} mb={3}>
            <Avatar
              sx={{ width: 80, height: 80 }}
              src={userProfile?.avatar_url || ''}
            >
              {user?.username?.charAt(0).toUpperCase()}
            </Avatar>
            
            <Box>
              <Typography variant="h6">
                {user?.username}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {user?.email}
              </Typography>
              
              {user?.is_premium && (
                <Chip
                  label="Premium Member"
                  color="primary"
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          </Box>
          
          <Button
            variant="outlined"
            startIcon={<PersonIcon />}
            onClick={() => setOpenProfileDialog(true)}
          >
            Edit Profile
          </Button>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Dietary Preferences
          </Typography>
          
          <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
            {userProfile?.dietary_tags?.map((tag) => (
              <Chip key={tag} label={tag} color="primary" />
            ))}
          </Box>
          
          <Typography variant="h6" gutterBottom>
            Allergens to Avoid
          </Typography>
          
          <Box display="flex" gap={1} flexWrap="wrap">
            {userProfile?.allergens?.map((allergen) => (
              <Chip key={allergen} label={allergen} color="error" />
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  const renderSecuritySection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Account Security
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Password
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={2}>
            Last changed: Never (recommended to change regularly)
          </Typography>
          
          <Button
            variant="outlined"
            startIcon={<SecurityIcon />}
            onClick={() => setOpenPasswordDialog(true)}
          >
            Change Password
          </Button>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Two-Factor Authentication
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={2}>
            Add an extra layer of security to your account
          </Typography>
          
          <FormControlLabel
            control={<Switch />}
            label="Enable Two-Factor Authentication"
            disabled={!user?.is_premium} // Premium feature
          />
          
          {!user?.is_premium && (
            <Typography variant="caption" color="textSecondary">
              Two-factor authentication is a premium feature
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );

  const renderNotificationsSection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Notification Settings
      </Typography>
      
      <Card>
        <CardContent>
          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications}
                  onChange={(e) => setSettings({...settings, notifications: e.target.checked})}
                />
              }
              label="Push Notifications"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.email_notifications}
                  onChange={(e) => setSettings({...settings, email_notifications: e.target.checked})}
                />
              }
              label="Email Notifications"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.push_notifications}
                  onChange={(e) => setSettings({...settings, push_notifications: e.target.checked})}
                />
              }
              label="Browser Push Notifications"
            />
          </FormGroup>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="h6" gutterBottom>
            Notification Types
          </Typography>
          
          <FormGroup>
            <FormControlLabel
              control={<Checkbox />}
              label="Item expiration alerts"
            />
            <FormControlLabel
              control={<Checkbox />}
              label="Low stock warnings"
            />
            <FormControlLabel
              control={<Checkbox />}
              label="Meal plan reminders"
            />
            <FormControlLabel
              control={<Checkbox />}
              label="Recipe suggestions"
            />
            <FormControlLabel
              control={<Checkbox />}
              label="Achievement notifications"
            />
          </FormGroup>
        </CardContent>
      </Card>
    </Box>
  );

  const renderPreferencesSection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Preferences
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Appearance
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={settings.dark_mode}
                onChange={(e) => setSettings({...settings, dark_mode: e.target.checked})}
                icon={<LightModeIcon />}
                checkedIcon={<DarkModeIcon />}
              />
            }
            label="Dark Mode"
          />
        </CardContent>
      </Card>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Features
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={settings.ai_suggestions}
                onChange={(e) => setSettings({...settings, ai_suggestions: e.target.checked})}
                disabled={!user?.is_premium}
              />
            }
            label="AI Recipe Suggestions"
          />
          
          {!user?.is_premium && (
            <Typography variant="caption" color="textSecondary">
              AI features are available with Premium subscription
            </Typography>
          )}
          
          <FormControlLabel
            control={
              <Switch
                checked={settings.data_sharing}
                onChange={(e) => setSettings({...settings, data_sharing: e.target.checked})}
              />
            }
            label="Help improve the app with usage data"
          />
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Units & Measurements
          </Typography>
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Default Unit System</InputLabel>
            <Select value="metric" onChange={() => {}}>
              <MenuItem value="metric">Metric (kg, L)</MenuItem>
              <MenuItem value="imperial">Imperial (lb, gal)</MenuItem>
            </Select>
          </FormControl>
          
          <FormControlLabel
            control={<Checkbox />}
            label="Show nutrition information"
          />
        </CardContent>
      </Card>
    </Box>
  );

  const renderHouseholdSection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Household Settings
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Household
          </Typography>
          
          {user?.household_id ? (
            <Box>
              <Typography variant="body1">
                {user.household?.name || 'My Household'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Member since: {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
              </Typography>
              
              <Button
                variant="outlined"
                startIcon={<GroupIcon />}
                sx={{ mt: 2 }}
                onClick={() => console.log('Manage household members')}
              >
                Manage Members
              </Button>
            </Box>
          ) : (
            <Box>
              <Typography variant="body2" color="textSecondary" mb={2}>
                You're not part of a household yet. Create one to share recipes and meal plans with family members.
              </Typography>
              
              <Button
                variant="contained"
                startIcon={<GroupIcon />}
                onClick={() => console.log('Create household')}
              >
                Create Household
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Sharing Settings
          </Typography>
          
          <FormGroup>
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Allow family members to edit my recipes"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="Share meal plans with household"
            />
            <FormControlLabel
              control={<Switch />}
              label="Share shopping lists with household"
            />
          </FormGroup>
        </CardContent>
      </Card>
    </Box>
  );

  const renderBillingSection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Billing & Plans
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Plan
              </Typography>
              
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Chip
                  label={user?.is_premium ? 'Premium' : 'Free'}
                  color={user?.is_premium ? 'primary' : 'default'}
                  size="medium"
                />
                
                {user?.is_premium && (
                  <Typography variant="body2" color="textSecondary">
                    Member since: {new Date().toLocaleDateString()}
                  </Typography>
                )}
              </Box>
              
              <Typography variant="body2" color="textSecondary" mb={2}>
                {user?.is_premium
                  ? 'Unlimited recipes, AI meal planning, advanced features'
                  : 'Basic features, limited to 50 recipes, no AI features'}
              </Typography>
              
              {!user?.is_premium && (
                <Button
                  variant="contained"
                  startIcon={<PaymentIcon />}
                  onClick={() => console.log('Upgrade to premium')}
                >
                  Upgrade to Premium
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Premium Features
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <AutoIcon color={user?.is_premium ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText primary="AI Recipe Suggestions" />
                  {user?.is_premium && <CheckIcon color="success" />}
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <GroupIcon color={user?.is_premium ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText primary="Family Sharing (5 members)" />
                  {user?.is_premium && <CheckIcon color="success" />}
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <RestaurantIcon color={user?.is_premium ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText primary="Unlimited Recipes" />
                  {user?.is_premium && <CheckIcon color="success" />}
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <StorageIcon color={user?.is_premium ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText primary="Advanced Analytics" />
                  {user?.is_premium && <CheckIcon color="success" />}
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderDataSection = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Data & Privacy
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Export
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={2}>
            Download all your data including recipes, meal plans, and inventory
          </Typography>
          
          <Button
            variant="outlined"
            startIcon={<BackupIcon />}
            onClick={handleExportData}
          >
            Export My Data
          </Button>
        </CardContent>
      </Card>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Privacy Settings
          </Typography>
          
          <FormGroup>
            <FormControlLabel
              control={<Switch />}
              label="Allow anonymous usage analytics"
            />
            <FormControlLabel
              control={<Switch />}
              label="Share anonymized recipe data for research"
            />
            <FormControlLabel
              control={<Switch />}
              label="Allow personalized ads (if shown)"
            />
          </FormGroup>
        </CardContent>
      </Card>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Account Deletion
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={2}>
            Permanently delete your account and all associated data. This action cannot be undone.
          </Typography>
          
          <Button
            variant="outlined"
            color="error"
            onClick={handleDeleteAccount}
          >
            Delete Account
          </Button>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Storage
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={2}>
            Your data is stored securely and privately on your self-hosted instance.
          </Typography>
          
          <List dense>
            <ListItem>
              <ListItemText
                primary="Total Recipes"
                secondary="24 recipes"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Inventory Items"
                secondary="156 items"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Meal Plans"
                secondary="12 plans"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Storage Used"
                secondary="2.3 MB"
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );

  const renderContent = () => {
    switch (selectedTab) {
      case 0:
        return renderProfileSection();
      case 1:
        return renderSecuritySection();
      case 2:
        return renderNotificationsSection();
      case 3:
        return renderPreferencesSection();
      case 4:
        return renderHouseholdSection();
      case 5:
        return renderBillingSection();
      case 6:
        return renderDataSection();
      default:
        return renderProfileSection();
    }
  };

  return (
    <Box display="flex" minHeight="100vh">
      {/* Sidebar */}
      <Box
        sx={{
          width: 250,
          bgcolor: 'background.paper',
          borderRight: '1px solid',
          borderColor: 'divider',
          p: 2
        }}
      >
        <Typography variant="h6" gutterBottom>
          Settings
        </Typography>
        
        <List>
          {menuItems.map((item, index) => (
            <ListItemButton
              key={index}
              selected={selectedTab === index}
              onClick={() => setSelectedTab(index)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          ))}
        </List>
      </Box>
      
      {/* Main Content */}
      <Box flex={1} p={3}>
        {renderContent()}
      </Box>
      
      {/* Profile Edit Dialog */}
      <Dialog open={openProfileDialog} onClose={() => setOpenProfileDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Display Name"
            fullWidth
            value={profileData.display_name}
            onChange={(e) => setProfileData({...profileData, display_name: e.target.value})}
          />
          
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            Dietary Preferences
          </Typography>
          
          <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
            {dietaryOptions.map(option => (
              <Chip
                key={option}
                label={option}
                clickable
                color={profileData.dietary_tags.includes(option) ? 'primary' : 'default'}
                onClick={() => {
                  setProfileData(prev => ({
                    ...prev,
                    dietary_tags: prev.dietary_tags.includes(option)
                      ? prev.dietary_tags.filter(tag => tag !== option)
                      : [...prev.dietary_tags, option]
                  }));
                }}
              />
            ))}
          </Box>
          
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            Allergens
          </Typography>
          
          <Box display="flex" gap={1} flexWrap="wrap">
            {allergenOptions.map(option => (
              <Chip
                key={option}
                label={option}
                clickable
                color={profileData.allergens.includes(option) ? 'error' : 'default'}
                onClick={() => {
                  setProfileData(prev => ({
                    ...prev,
                    allergens: prev.allergens.includes(option)
                      ? prev.allergens.filter(tag => tag !== option)
                      : [...prev.allergens, option]
                  }));
                }}
              />
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenProfileDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveProfile} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
      
      {/* Password Change Dialog */}
      <Dialog open={openPasswordDialog} onClose={() => setOpenPasswordDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Current Password"
            type="password"
            fullWidth
            value={passwordData.current_password}
            onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
          />
          
          <TextField
            margin="dense"
            label="New Password"
            type="password"
            fullWidth
            value={passwordData.new_password}
            onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
          />
          
          <TextField
            margin="dense"
            label="Confirm New Password"
            type="password"
            fullWidth
            value={passwordData.confirm_password}
            onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPasswordDialog(false)}>Cancel</Button>
          <Button onClick={handleChangePassword} variant="contained">Change Password</Button>
        </DialogActions>
      </Dialog>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({...snackbar, open: false})}
      >
        <Alert
          onClose={() => setSnackbar({...snackbar, open: false})}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;