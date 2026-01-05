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
  ListItemIcon,
  Checkbox,
  Divider,
  Alert,
  Snackbar,
  CircularProgress,
  Tabs,
  Tab,
  Badge,
  Collapse
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ShoppingCart as ShoppingIcon,
  CheckCircle as CheckIcon,
  CompareArrows as CompareIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Category as CategoryIcon,
  PriceCheck as PriceIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { shoppingService } from '../services/api';
import { ShoppingList, ShoppingListItem } from '../types';

const ShoppingLists: React.FC = () => {
  const { user } = useAuth();
  const [shoppingLists, setShoppingLists] = useState<ShoppingList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [viewingList, setViewingList] = useState<ShoppingList | null>(null);
  const [expandedLists, setExpandedLists] = useState<Set<string>>(new Set());
  const [newList, setNewList] = useState({
    name: '',
    description: '',
    tags: []
  });
  const [newItem, setNewItem] = useState({
    name: '',
    quantity: 1,
    unit: 'pcs',
    category: 'other',
    estimated_price: 0
  });
  const [openAddItemDialog, setOpenAddItemDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });

  useEffect(() => {
    loadShoppingLists();
  }, []);

  const loadShoppingLists = async () => {
    try {
      setLoading(true);
      const data = await shoppingService.getShoppingLists();
      setShoppingLists(data);
      setError(null);
    } catch (err) {
      setError('Failed to load shopping lists');
      console.error('Error loading shopping lists:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateList = async () => {
    try {
      const list = await shoppingService.createShoppingList(newList);
      setShoppingLists([...shoppingLists, list]);
      setOpenCreateDialog(false);
      setNewList({ name: '', description: '', tags: [] });
      setSnackbar({
        open: true,
        message: 'Shopping list created successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to create shopping list',
        severity: 'error'
      });
    }
  };

  const handleAddItem = async (listId: string) => {
    try {
      const item = await shoppingService.addShoppingListItem(listId, newItem);
      
      // Update the list in state
      setShoppingLists(lists => 
        lists.map(list => 
          list.id === listId 
            ? { ...list, items: [...(list.items || []), item] }
            : list
        )
      );
      
      setOpenAddItemDialog(false);
      setNewItem({ name: '', quantity: 1, unit: 'pcs', category: 'other', estimated_price: 0 });
      setSnackbar({
        open: true,
        message: 'Item added successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to add item',
        severity: 'error'
      });
    }
  };

  const handleToggleItem = async (listId: string, item: ShoppingListItem) => {
    try {
      const updatedItem = await shoppingService.updateShoppingListItem(listId, item.id, {
        is_completed: !item.is_completed
      });
      
      // Update the item in state
      setShoppingLists(lists =>
        lists.map(list =>
          list.id === listId
            ? {
                ...list,
                items: list.items?.map(i =>
                  i.id === item.id ? updatedItem : i
                )
              }
            : list
        )
      );
    } catch (err) {
      console.error('Error toggling item:', err);
    }
  };

  const handleViewList = (list: ShoppingList) => {
    setViewingList(list);
    setOpenViewDialog(true);
  };

  const handleDeleteList = async (listId: string) => {
    try {
      await shoppingService.deleteShoppingList(listId);
      setShoppingLists(lists => lists.filter(list => list.id !== listId));
      setSnackbar({
        open: true,
        message: 'Shopping list deleted successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to delete shopping list',
        severity: 'error'
      });
    }
  };

  const handleComparePrices = async (listId: string) => {
    try {
      const comparison = await shoppingService.comparePrices(listId);
      
      // Show price comparison results
      setSnackbar({
        open: true,
        message: `Best store: ${comparison.best_store}. Potential savings: $${comparison.total_estimated_savings.toFixed(2)}`,
        severity: 'info'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to compare prices',
        severity: 'error'
      });
    }
  };

  const handleOptimizeList = async (listId: string) => {
    try {
      const optimization = await shoppingService.optimizeShoppingList(listId);
      
      setSnackbar({
        open: true,
        message: `List optimized. ${optimization.total_items} items organized by store sections.`,
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to optimize list',
        severity: 'error'
      });
    }
  };

  const toggleListExpansion = (listId: string) => {
    const newExpanded = new Set(expandedLists);
    if (newExpanded.has(listId)) {
      newExpanded.delete(listId);
    } else {
      newExpanded.add(listId);
    }
    setExpandedLists(newExpanded);
  };

  const getCompletedCount = (items?: ShoppingListItem[]) => {
    if (!items) return 0;
    return items.filter(item => item.is_completed).length;
  };

  const categories = ['produce', 'dairy', 'meat', 'pantry', 'frozen', 'bakery', 'other'];

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
        Shopping Lists
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
          Create List
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<ShoppingIcon />}
          onClick={() => console.log('Quick Add Mode')}
        >
          Quick Add
        </Button>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Active Lists" />
          <Tab label="All Lists" />
          <Tab label="Templates" />
        </Tabs>
      </Box>
      
      <Grid container spacing={3}>
        {shoppingLists.map((list) => {
          const completedCount = getCompletedCount(list.items);
          const totalCount = list.items?.length || 0;
          const isExpanded = expandedLists.has(list.id);
          
          return (
            <Grid item xs={12} md={6} key={list.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box>
                      <Typography variant="h6">
                        {list.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {list.description}
                      </Typography>
                    </Box>
                    
                    <Badge badgeContent={completedCount} color="success">
                      <Chip
                        label={`${completedCount}/${totalCount}`}
                        variant="outlined"
                        size="small"
                      />
                    </Badge>
                  </Box>
                  
                  {list.tags && list.tags.length > 0 && (
                    <Box mb={2}>
                      {list.tags.map((tag, index) => (
                        <Chip key={index} label={tag} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </Box>
                  )}
                  
                  <Box display="flex" alignItems="center" gap={1}>
                    <ShoppingIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="textSecondary">
                      {totalCount} items
                    </Typography>
                    
                    {list.is_active !== undefined && (
                      <Chip
                        label={list.is_active ? 'Active' : 'Completed'}
                        color={list.is_active ? 'success' : 'default'}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Box>
                  
                  {isExpanded && list.items && list.items.length > 0 && (
                    <Box mt={2}>
                      <Divider sx={{ mb: 1 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Items:
                      </Typography>
                      <List dense>
                        {list.items.slice(0, 5).map((item) => (
                          <ListItem key={item.id} disablePadding>
                            <ListItemIcon>
                              <Checkbox
                                edge="start"
                                checked={item.is_completed}
                                onChange={() => handleToggleItem(list.id, item)}
                                size="small"
                              />
                            </ListItemIcon>
                            <ListItemText
                              primary={`${item.name} (${item.quantity} ${item.unit})`}
                              secondary={item.category}
                              sx={{
                                textDecoration: item.is_completed ? 'line-through' : 'none',
                                color: item.is_completed ? 'text.secondary' : 'text.primary'
                              }}
                            />
                          </ListItem>
                        ))}
                        {list.items.length > 5 && (
                          <ListItem>
                            <ListItemText
                              primary={`... and ${list.items.length - 5} more items`}
                              secondary="View full list for details"
                            />
                          </ListItem>
                        )}
                      </List>
                    </Box>
                  )}
                </CardContent>
                
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => handleViewList(list)}
                    startIcon={<ShoppingIcon />}
                  >
                    View List
                  </Button>
                  
                  <IconButton
                    size="small"
                    onClick={() => toggleListExpansion(list.id)}
                  >
                    {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                  
                  <Box flexGrow={1} />
                  
                  <Tooltip title="Compare Prices">
                    <IconButton
                      size="small"
                      onClick={() => handleComparePrices(list.id)}
                    >
                      <CompareIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Optimize List">
                    <IconButton
                      size="small"
                      onClick={() => handleOptimizeList(list.id)}
                    >
                      <CategoryIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Add Item">
                    <IconButton
                      size="small"
                      onClick={() => {
                        setViewingList(list);
                        setOpenAddItemDialog(true);
                      }}
                    >
                      <AddIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Delete List">
                    <IconButton size="small" color="error" onClick={() => handleDeleteList(list.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      
      {shoppingLists.length === 0 && (
        <Box textAlign="center" py={5}>
          <Typography variant="h6" color="textSecondary">
            No shopping lists found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Create your first shopping list to get started
          </Typography>
        </Box>
      )}
      
      {/* Create List Dialog */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Shopping List</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="List Name"
            fullWidth
            value={newList.name}
            onChange={(e) => setNewList({...newList, name: e.target.value})}
          />
          
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newList.description}
            onChange={(e) => setNewList({...newList, description: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateList} variant="contained">Create List</Button>
        </DialogActions>
      </Dialog>
      
      {/* Add Item Dialog */}
      <Dialog open={openAddItemDialog} onClose={() => setOpenAddItemDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Item to {viewingList?.name}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Item Name"
            fullWidth
            value={newItem.name}
            onChange={(e) => setNewItem({...newItem, name: e.target.value})}
          />
          
          <Box display="flex" gap={2}>
            <TextField
              margin="dense"
              label="Quantity"
              type="number"
              value={newItem.quantity}
              onChange={(e) => setNewItem({...newItem, quantity: parseFloat(e.target.value)})}
            />
            
            <TextField
              margin="dense"
              label="Unit"
              value={newItem.unit}
              onChange={(e) => setNewItem({...newItem, unit: e.target.value})}
            />
          </Box>
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Category</InputLabel>
            <Select
              value={newItem.category}
              onChange={(e) => setNewItem({...newItem, category: e.target.value})}
            >
              {categories.map(cat => (
                <MenuItem key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            label="Estimated Price"
            type="number"
            value={newItem.estimated_price}
            onChange={(e) => setNewItem({...newItem, estimated_price: parseFloat(e.target.value)})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddItemDialog(false)}>Cancel</Button>
          <Button 
            onClick={() => viewingList && handleAddItem(viewingList.id)} 
            variant="contained"
          >
            Add Item
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* View List Dialog */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{viewingList?.name}</DialogTitle>
        <DialogContent>
          {viewingList && (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {viewingList.description}
              </Typography>
              
              <Box display="flex" gap={2} mb={2}>
                <Chip
                  label={`${getCompletedCount(viewingList.items)}/${viewingList.items?.length || 0} completed`}
                  color="default"
                />
                
                <Chip
                  label={viewingList.is_active ? 'Active' : 'Completed'}
                  color={viewingList.is_active ? 'success' : 'default'}
                />
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Price</TableCell>
                      <TableCell>Completed</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {viewingList.items?.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <Typography
                            sx={{
                              textDecoration: item.is_completed ? 'line-through' : 'none',
                              color: item.is_completed ? 'text.secondary' : 'text.primary'
                            }}
                          >
                            {item.name}
                          </Typography>
                          {item.notes && (
                            <Typography variant="caption" color="textSecondary">
                              {item.notes}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {item.quantity} {item.unit}
                        </TableCell>
                        <TableCell>
                          <Chip label={item.category} size="small" />
                        </TableCell>
                        <TableCell>
                          ${item.estimated_price?.toFixed(2) || '0.00'}
                        </TableCell>
                        <TableCell>
                          <Checkbox
                            checked={item.is_completed}
                            onChange={() => handleToggleItem(viewingList.id, item)}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenViewDialog(false)}>Close</Button>
          <Button
            variant="contained"
            startIcon={<CompareIcon />}
            onClick={() => viewingList && handleComparePrices(viewingList.id)}
          >
            Compare Prices
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

export default ShoppingLists;