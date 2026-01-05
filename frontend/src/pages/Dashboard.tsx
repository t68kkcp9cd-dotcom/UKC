import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  Button,
} from '@mui/material';
import {
  Kitchen,
  Restaurant,
  CalendarToday,
  ShoppingCart,
  Warning,
  TrendingUp,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import apiService from '../services/api';
import { InventoryItem, Recipe, MealPlan, ShoppingList } from '../types';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalItems: 0,
    expiringItems: 0,
    totalRecipes: 0,
    activeLists: 0,
  });

  // Fetch dashboard data
  const { data: inventoryItems, isLoading: inventoryLoading } = useQuery(
    ['inventory', { limit: 5 }],
    () => apiService.getInventoryItems({ limit: 5 }),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  const { data: recipes, isLoading: recipesLoading } = useQuery(
    ['recipes', { limit: 5 }],
    () => apiService.getRecipes({ limit: 5 }),
    {
      staleTime: 5 * 60 * 1000,
    }
  );

  const { data: mealPlans, isLoading: mealPlansLoading } = useQuery(
    ['meal-plans', { limit: 3 }],
    () => apiService.getMealPlans({ limit: 3 }),
    {
      staleTime: 5 * 60 * 1000,
    }
  );

  const { data: shoppingLists, isLoading: listsLoading } = useQuery(
    ['shopping-lists', { is_active: true, limit: 3 }],
    () => apiService.getShoppingLists({ is_active: true, limit: 3 }),
    {
      staleTime: 5 * 60 * 1000,
    }
  );

  const { data: wasteForecast } = useQuery(
    ['waste-forecast'],
    () => apiService.getWasteForecast(7),
    {
      staleTime: 30 * 60 * 1000, // 30 minutes
    }
  );

  useEffect(() => {
    if (inventoryItems?.data) {
      const expiring = inventoryItems.data.filter(
        (item) => item.days_until_expiration && item.days_until_expiration <= 3
      ).length;
      setStats((prev) => ({ ...prev, totalItems: inventoryItems.total, expiringItems: expiring }));
    }
    if (recipes?.total !== undefined) {
      setStats((prev) => ({ ...prev, totalRecipes: recipes.total }));
    }
    if (shoppingLists?.total !== undefined) {
      setStats((prev) => ({ ...prev, activeLists: shoppingLists.total }));
    }
  }, [inventoryItems, recipes, shoppingLists]);

  const StatCard = ({ title, value, icon, color, onClick }: any) => (
    <Card
      sx={{
        height: 120,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: onClick ? 'scale(1.02)' : 'none',
        },
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
          </Box>
          <Box sx={{ fontSize: 40, opacity: 0.7 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );

  const ExpiringAlert = () => {
    if (!wasteForecast || wasteForecast.total_items_at_risk === 0) return null;

    return (
      <Alert
        severity="warning"
        icon={<Warning />}
        action={
          <Button color="inherit" size="small" onClick={() => window.location.href = '/inventory'}>
            View Items
          </Button>
        }
      >
        <Typography variant="h6">Items Expiring Soon!</Typography>
        <Typography variant="body2">
          {wasteForecast.total_items_at_risk} items are expiring within the next 7 days.
          Estimated waste value: ${wasteForecast.estimated_waste_value.toFixed(2)}
        </Typography>
      </Alert>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Expiring Items Alert */}
      <Box mb={3}>
        <ExpiringAlert />
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Items"
            value={stats.totalItems}
            icon={<Kitchen />}
            color="primary.main"
            onClick={() => window.location.href = '/inventory'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expiring Soon"
            value={stats.expiringItems}
            icon={<Warning />}
            color="error.main"
            onClick={() => window.location.href = '/inventory?expires_before=3'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Recipes"
            value={stats.totalRecipes}
            icon={<Restaurant />}
            color="secondary.main"
            onClick={() => window.location.href = '/recipes'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Lists"
            value={stats.activeLists}
            icon={<ShoppingCart />}
            color="success.main"
            onClick={() => window.location.href = '/shopping'}
          />
        </Grid>
      </Grid>

      {/* Recent Items */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Inventory Items
            </Typography>
            {inventoryLoading ? (
              <Typography>Loading...</Typography>
            ) : (
              <List>
                {inventoryItems?.data?.slice(0, 5).map((item) => (
                  <ListItem key={item.id} divider>
                    <ListItemText
                      primary={item.name}
                      secondary={`${item.quantity} ${item.unit} • ${item.location}`}
                    />
                    {item.days_until_expiration !== undefined && (
                      <Chip
                        label={`${item.days_until_expiration} days`}
                        color={item.days_until_expiration <= 3 ? 'error' : 'default'}
                        size="small"
                      />
                    )}
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Recipes
            </Typography>
            {recipesLoading ? (
              <Typography>Loading...</Typography>
            ) : (
              <List>
                {recipes?.data?.slice(0, 5).map((recipe) => (
                  <ListItem key={recipe.id} divider>
                    <ListItemText
                      primary={recipe.title}
                      secondary={`${recipe.difficulty} • ${recipe.servings} servings`}
                    />
                    {recipe.average_rating && (
                      <Chip
                        label={`⭐ ${recipe.average_rating.toFixed(1)}`}
                        size="small"
                      />
                    )}
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Upcoming Meals
            </Typography>
            {mealPlansLoading ? (
              <Typography>Loading...</Typography>
            ) : (
              <List>
                {mealPlans?.data?.slice(0, 5).map((plan) => (
                  <ListItem key={plan.id} divider>
                    <ListItemText
                      primary={plan.plan_name}
                      secondary={`${plan.start_date} to ${plan.end_date}`}
                    />
                    <Chip
                      label={`${plan.entries.length} meals`}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Active Shopping Lists
            </Typography>
            {listsLoading ? (
              <Typography>Loading...</Typography>
            ) : (
              <List>
                {shoppingLists?.data?.slice(0, 5).map((list) => (
                  <ListItem key={list.id} divider>
                    <ListItemText
                      primary={list.list_name}
                      secondary={list.store?.name || 'No store selected'}
                    />
                    <Chip
                      label={`${list.items.filter(item => !item.is_checked).length} items`}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;