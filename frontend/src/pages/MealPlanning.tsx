import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Alert,
  Snackbar,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CalendarToday as CalendarIcon,
  Restaurant as RestaurantIcon,
  AutoAwesome as AutoIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { mealPlanService, aiService } from '../services/api';
import { MealPlan, MealPlanEntry } from '../types';

const MealPlanning: React.FC = () => {
  const { user } = useAuth();
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [currentWeekPlan, setCurrentWeekPlan] = useState<MealPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedWeek, setSelectedWeek] = useState<Date>(new Date());
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [viewingPlan, setViewingPlan] = useState<MealPlan | null>(null);
  const [newPlan, setNewPlan] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    tags: []
  });
  const [aiGenerating, setAiGenerating] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });

  useEffect(() => {
    loadMealPlans();
    loadCurrentWeekPlan();
  }, []);

  const loadMealPlans = async () => {
    try {
      setLoading(true);
      const data = await mealPlanService.getMealPlans();
      setMealPlans(data);
      setError(null);
    } catch (err) {
      setError('Failed to load meal plans');
      console.error('Error loading meal plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentWeekPlan = async () => {
    try {
      const plan = await mealPlanService.getCurrentWeekPlan();
      setCurrentWeekPlan(plan);
    } catch (err) {
      console.error('Error loading current week plan:', err);
    }
  };

  const handleCreatePlan = async () => {
    try {
      const plan = await mealPlanService.createMealPlan(newPlan);
      setMealPlans([...mealPlans, plan]);
      setOpenCreateDialog(false);
      setNewPlan({
        name: '',
        description: '',
        start_date: '',
        end_date: '',
        tags: []
      });
      setSnackbar({
        open: true,
        message: 'Meal plan created successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to create meal plan',
        severity: 'error'
      });
    }
  };

  const handleGenerateWithAI = async () => {
    if (!user?.is_premium) {
      setSnackbar({
        open: true,
        message: 'AI meal planning is a premium feature',
        severity: 'info'
      });
      return;
    }
    
    setAiGenerating(true);
    try {
      const aiPlan = await aiService.generateMealPlan({
        days: 7,
        dietary_preferences: [],
        budget_range: 'medium'
      });
      
      if (aiPlan.meal_plan) {
        setMealPlans([...mealPlans, aiPlan.meal_plan]);
        setSnackbar({
          open: true,
          message: 'AI meal plan generated successfully',
          severity: 'success'
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to generate AI meal plan',
        severity: 'error'
      });
    } finally {
      setAiGenerating(false);
    }
  };

  const getWeekDates = (date: Date) => {
    const startOfWeek = new Date(date);
    startOfWeek.setDate(date.getDate() - date.getDay());
    
    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(startOfWeek);
      day.setDate(startOfWeek.getDate() + i);
      days.push(day);
    }
    return days;
  };

  const weekDates = getWeekDates(selectedWeek);
  const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];

  const renderMealPlanGrid = (plan: MealPlan) => {
    const days = getWeekDates(new Date(plan.start_date));
    
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Meal Type</TableCell>
              {days.map((day, index) => (
                <TableCell key={index}>
                  {day.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {mealTypes.map(mealType => (
              <TableRow key={mealType}>
                <TableCell>
                  <Typography variant="subtitle2" sx={{ textTransform: 'capitalize' }}>
                    {mealType}
                  </Typography>
                </TableCell>
                {days.map((day, dayIndex) => {
                  const entry = plan.entries?.find(
                    e => e.meal_type === mealType && 
                    new Date(e.date).toDateString() === day.toDateString()
                  );
                  
                  return (
                    <TableCell key={dayIndex}>
                      {entry ? (
                        <Card variant="outlined" sx={{ bgcolor: 'primary.light', color: 'white' }}>
                          <CardContent sx={{ p: 1 }}>
                            <Typography variant="body2" fontWeight="medium">
                              {entry.recipe_name}
                            </Typography>
                            {entry.estimated_prep_time && (
                              <Typography variant="caption">
                                {entry.estimated_prep_time} min
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      ) : (
                        <Box
                          sx={{
                            width: '100%',
                            height: 60,
                            border: '1px dashed #ccc',
                            borderRadius: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            '&:hover': {
                              bgcolor: 'action.hover'
                            }
                          }}
                          onClick={() => console.log('Add meal for', mealType, day.toDateString())}
                        >
                          <AddIcon fontSize="small" color="action" />
                        </Box>
                      )}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Meal Planning
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box display="flex" gap={2} mb={3}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenCreateDialog(true)}
        >
          Create Plan
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<AutoIcon />}
          onClick={handleGenerateWithAI}
          disabled={aiGenerating}
        >
          {aiGenerating ? <CircularProgress size={20} /> : 'Generate with AI'}
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<CalendarIcon />}
          onClick={() => {
            const nextWeek = new Date(selectedWeek);
            nextWeek.setDate(selectedWeek.getDate() + 7);
            setSelectedWeek(nextWeek);
          }}
        >
          Next Week
        </Button>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Current Week" />
          <Tab label="All Plans" />
          <Tab label="AI Suggestions" />
        </Tabs>
      </Box>
      
      {selectedTab === 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            This Week's Meal Plan
          </Typography>
          
          {currentWeekPlan ? (
            <Box>
              <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                {currentWeekPlan.name}
              </Typography>
              {renderMealPlanGrid(currentWeekPlan)}
            </Box>
          ) : (
            <Box textAlign="center" py={5}>
              <Typography variant="h6" color="textSecondary">
                No meal plan for this week
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Create a meal plan or use AI to generate one
              </Typography>
            </Box>
          )}
        </Box>
      )}
      
      {selectedTab === 1 && (
        <Grid container spacing={3}>
          {mealPlans.map((plan) => (
            <Grid item xs={12} md={6} key={plan.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6">
                      {plan.name}
                    </Typography>
                    <Chip
                      label={plan.is_active ? 'Active' : 'Inactive'}
                      color={plan.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {plan.description}
                  </Typography>
                  
                  <Box display="flex" gap={2} mb={2}>
                    <Box display="flex" alignItems="center">
                      <CalendarIcon fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2">
                        {new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                    
                    <Box display="flex" alignItems="center">
                      <ScheduleIcon fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2">
                        {plan.entries?.length || 0} meals
                      </Typography>
                    </Box>
                  </Box>
                  
                  {plan.tags && plan.tags.length > 0 && (
                    <Box mb={2}>
                      {plan.tags.map((tag, index) => (
                        <Chip key={index} label={tag} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </Box>
                  )}
                </CardContent>
                
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => handleViewPlan(plan)}
                    startIcon={<RestaurantIcon />}
                  >
                    View Plan
                  </Button>
                  
                  <Box flexGrow={1} />
                  
                  <IconButton size="small">
                    <EditIcon />
                  </IconButton>
                  
                  <IconButton size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {selectedTab === 2 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            AI Meal Suggestions
          </Typography>
          
          <Grid container spacing={2}>
            {['breakfast', 'lunch', 'dinner'].map(mealType => (
              <Grid item xs={12} md={4} key={mealType}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ textTransform: 'capitalize' }}>
                      {mealType} Ideas
                    </Typography>
                    
                    <List>
                      {['Overnight Oats', 'Avocado Toast', 'Smoothie Bowl', 'Greek Yogurt Parfait'].map((suggestion, index) => (
                        <ListItem key={index} disablePadding>
                          <ListItemButton>
                            <ListItemText primary={suggestion} />
                          </ListItemButton>
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Create Plan Dialog */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Meal Plan</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Plan Name"
            fullWidth
            value={newPlan.name}
            onChange={(e) => setNewPlan({...newPlan, name: e.target.value})}
          />
          
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newPlan.description}
            onChange={(e) => setNewPlan({...newPlan, description: e.target.value})}
          />
          
          <Box display="flex" gap={2}>
            <TextField
              margin="dense"
              label="Start Date"
              type="date"
              fullWidth
              value={newPlan.start_date}
              onChange={(e) => setNewPlan({...newPlan, start_date: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
            
            <TextField
              margin="dense"
              label="End Date"
              type="date"
              fullWidth
              value={newPlan.end_date}
              onChange={(e) => setNewPlan({...newPlan, end_date: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreatePlan} variant="contained">Create Plan</Button>
        </DialogActions>
      </Dialog>
      
      {/* View Plan Dialog */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>{viewingPlan?.name}</DialogTitle>
        <DialogContent>
          {viewingPlan && renderMealPlanGrid(viewingPlan)}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<EditIcon />}>
            Edit Plan
          </Button>
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

export default MealPlanning;