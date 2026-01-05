import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
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
  Rating,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  Snackbar,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Restaurant as RestaurantIcon,
  Timer as TimerIcon,
  People as PeopleIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { recipeService } from '../services/api';
import { Recipe, RecipeCreate } from '../types';

const Recipes: React.FC = () => {
  const { user } = useAuth();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedCuisine, setSelectedCuisine] = useState<string>('all');
  const [selectedTab, setSelectedTab] = useState(0);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [viewingRecipe, setViewingRecipe] = useState<Recipe | null>(null);
  const [newRecipe, setNewRecipe] = useState<RecipeCreate>({
    title: '',
    description: '',
    category: 'main',
    cuisine_type: 'general',
    prep_time: 30,
    cook_time: 30,
    servings: 4,
    difficulty: 'medium',
    is_public: false,
    ingredients: [],
    steps: []
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });

  useEffect(() => {
    loadRecipes();
  }, []);

  const loadRecipes = async () => {
    try {
      setLoading(true);
      const data = await recipeService.getRecipes();
      setRecipes(data);
      setError(null);
    } catch (err) {
      setError('Failed to load recipes');
      console.error('Error loading recipes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRecipe = async () => {
    try {
      const recipe = await recipeService.createRecipe(newRecipe);
      setRecipes([...recipes, recipe]);
      setOpenAddDialog(false);
      setNewRecipe({
        title: '',
        description: '',
        category: 'main',
        cuisine_type: 'general',
        prep_time: 30,
        cook_time: 30,
        servings: 4,
        difficulty: 'medium',
        is_public: false,
        ingredients: [],
        steps: []
      });
      setSnackbar({
        open: true,
        message: 'Recipe added successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to add recipe',
        severity: 'error'
      });
    }
  };

  const handleViewRecipe = (recipe: Recipe) => {
    setViewingRecipe(recipe);
    setOpenViewDialog(true);
  };

  const filteredRecipes = recipes.filter(recipe => {
    const matchesSearch = recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         recipe.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || recipe.category === selectedCategory;
    const matchesCuisine = selectedCuisine === 'all' || recipe.cuisine_type === selectedCuisine;
    return matchesSearch && matchesCategory && matchesCuisine;
  });

  const categories = ['all', 'appetizer', 'main', 'side', 'dessert', 'beverage', 'other'];
  const cuisines = ['all', 'italian', 'mexican', 'asian', 'american', 'mediterranean', 'indian', 'other'];
  const difficulties = ['easy', 'medium', 'hard'];

  const renderDifficulty = (difficulty: string) => {
    const colors = {
      easy: 'success',
      medium: 'warning', 
      hard: 'error'
    };
    return <Chip label={difficulty} color={colors[difficulty] as any} size="small" />;
  };

  const renderStars = (rating: number) => {
    return (
      <Box display="flex" alignItems="center">
        <Rating
          value={rating}
          readOnly
          size="small"
          icon={<StarIcon fontSize="small" />}
          emptyIcon={<StarBorderIcon fontSize="small" />}
        />
        <Typography variant="body2" color="textSecondary" ml={1}>
          ({rating.toFixed(1)})
        </Typography>
      </Box>
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
        Recipe Collection
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box display="flex" gap={2} mb={3}>
        <TextField
          placeholder="Search recipes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon />
          }}
          size="small"
        />
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Category</InputLabel>
          <Select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(cat => (
              <MenuItem key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Cuisine</InputLabel>
          <Select
            value={selectedCuisine}
            onChange={(e) => setSelectedCuisine(e.target.value)}
          >
            {cuisines.map(cuisine => (
              <MenuItem key={cuisine} value={cuisine}>
                {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenAddDialog(true)}
        >
          Add Recipe
        </Button>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="All Recipes" />
          <Tab label="My Recipes" />
          <Tab label="Favorites" />
          <Tab label="Recently Added" />
        </Tabs>
      </Box>
      
      <Grid container spacing={3}>
        {filteredRecipes.map((recipe) => (
          <Grid item xs={12} sm={6} md={4} key={recipe.id}>
            <Card>
              {recipe.image_url && (
                <CardMedia
                  component="img"
                  height="140"
                  image={recipe.image_url}
                  alt={recipe.title}
                />
              )}
              
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                  <Typography variant="h6" component="h3">
                    {recipe.title}
                  </Typography>
                  <Chip
                    label={recipe.category}
                    variant="outlined"
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {recipe.description}
                </Typography>
                
                <Box display="flex" gap={2} mb={1}>
                  <Box display="flex" alignItems="center">
                    <TimerIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <Typography variant="body2">
                      {recipe.prep_time + recipe.cook_time} min
                    </Typography>
                  </Box>
                  
                  <Box display="flex" alignItems="center">
                    <PeopleIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <Typography variant="body2">
                      {recipe.servings} servings
                    </Typography>
                  </Box>
                  
                  {recipe.cuisine_type && (
                    <Box display="flex" alignItems="center">
                      <LanguageIcon fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2">
                        {recipe.cuisine_type}
                      </Typography>
                    </Box>
                  )}
                </Box>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  {renderDifficulty(recipe.difficulty)}
                  {recipe.avg_rating && renderStars(recipe.avg_rating)}
                </Box>
              </CardContent>
              
              <CardActions>
                <Button
                  size="small"
                  onClick={() => handleViewRecipe(recipe)}
                  startIcon={<RestaurantIcon />}
                >
                  View Recipe
                </Button>
                
                <Box flexGrow={1} />
                
                {recipe.created_by === user?.id && (
                  <IconButton size="small">
                    <EditIcon />
                  </IconButton>
                )}
                
                {recipe.created_by === user?.id && (
                  <IconButton size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {filteredRecipes.length === 0 && (
        <Box textAlign="center" py={5}>
          <Typography variant="h6" color="textSecondary">
            No recipes found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Add your first recipe to get started
          </Typography>
        </Box>
      )}
      
      {/* Add Recipe Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Recipe</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Recipe Title"
            fullWidth
            value={newRecipe.title}
            onChange={(e) => setNewRecipe({...newRecipe, title: e.target.value})}
          />
          
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newRecipe.description}
            onChange={(e) => setNewRecipe({...newRecipe, description: e.target.value})}
          />
          
          <Box display="flex" gap={2}>
            <FormControl fullWidth margin="dense">
              <InputLabel>Category</InputLabel>
              <Select
                value={newRecipe.category}
                onChange={(e) => setNewRecipe({...newRecipe, category: e.target.value})}
              >
                {categories.slice(1).map(cat => (
                  <MenuItem key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="dense">
              <InputLabel>Cuisine</InputLabel>
              <Select
                value={newRecipe.cuisine_type}
                onChange={(e) => setNewRecipe({...newRecipe, cuisine_type: e.target.value})}
              >
                {cuisines.slice(1).map(cuisine => (
                  <MenuItem key={cuisine} value={cuisine}>
                    {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
          
          <Box display="flex" gap={2}>
            <TextField
              margin="dense"
              label="Prep Time (minutes)"
              type="number"
              value={newRecipe.prep_time}
              onChange={(e) => setNewRecipe({...newRecipe, prep_time: parseInt(e.target.value)})}
            />
            
            <TextField
              margin="dense"
              label="Cook Time (minutes)"
              type="number"
              value={newRecipe.cook_time}
              onChange={(e) => setNewRecipe({...newRecipe, cook_time: parseInt(e.target.value)})}
            />
            
            <TextField
              margin="dense"
              label="Servings"
              type="number"
              value={newRecipe.servings}
              onChange={(e) => setNewRecipe({...newRecipe, servings: parseInt(e.target.value)})}
            />
          </Box>
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Difficulty</InputLabel>
            <Select
              value={newRecipe.difficulty}
              onChange={(e) => setNewRecipe({...newRecipe, difficulty: e.target.value})}
            >
              {difficulties.map(diff => (
                <MenuItem key={diff} value={diff}>
                  {diff.charAt(0).toUpperCase() + diff.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button onClick={handleAddRecipe} variant="contained">Add Recipe</Button>
        </DialogActions>
      </Dialog>
      
      {/* View Recipe Dialog */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h5">{viewingRecipe?.title}</Typography>
            <Box>
              {viewingRecipe && renderDifficulty(viewingRecipe.difficulty)}
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {viewingRecipe && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Ingredients
                </Typography>
                <List>
                  {viewingRecipe.ingredients?.map((ingredient, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={`${ingredient.quantity} ${ingredient.unit || ''} ${ingredient.name}`}
                        secondary={ingredient.notes}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Instructions
                </Typography>
                {viewingRecipe.steps?.map((step, index) => (
                  <Accordion key={index} defaultExpanded={index === 0}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Step {step.step_number}</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography>{step.instruction}</Typography>
                      {step.duration && (
                        <Typography variant="body2" color="textSecondary" mt={1}>
                          Duration: {step.duration} minutes
                        </Typography>
                      )}
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<RestaurantIcon />}>
            Cook This Recipe
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

export default Recipes;