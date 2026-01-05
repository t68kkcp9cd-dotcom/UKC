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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CameraAlt as CameraIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { inventoryService } from '../services/api';
import { InventoryItem, ItemCategory } from '../types';

const Inventory: React.FC = () => {
  const { user } = useAuth();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);
  const [newItem, setNewItem] = useState({
    name: '',
    category: 'general' as ItemCategory,
    quantity: 1,
    unit: 'pcs',
    expiration_date: '',
    location: 'pantry',
    notes: ''
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      setLoading(true);
      const data = await inventoryService.getItems();
      setItems(data);
      setError(null);
    } catch (err) {
      setError('Failed to load inventory items');
      console.error('Error loading inventory:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async () => {
    try {
      const item = await inventoryService.createItem(newItem);
      setItems([...items, item]);
      setOpenAddDialog(false);
      setNewItem({
        name: '',
        category: 'general' as ItemCategory,
        quantity: 1,
        unit: 'pcs',
        expiration_date: '',
        location: 'pantry',
        notes: ''
      });
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

  const handleUpdateItem = async () => {
    if (!editingItem) return;
    
    try {
      const updatedItem = await inventoryService.updateItem(editingItem.id, editingItem);
      setItems(items.map(item => item.id === updatedItem.id ? updatedItem : item));
      setOpenEditDialog(false);
      setEditingItem(null);
      setSnackbar({
        open: true,
        message: 'Item updated successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to update item',
        severity: 'error'
      });
    }
  };

  const handleDeleteItem = async (itemId: string) => {
    try {
      await inventoryService.deleteItem(itemId);
      setItems(items.filter(item => item.id !== itemId));
      setSnackbar({
        open: true,
        message: 'Item deleted successfully',
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to delete item',
        severity: 'error'
      });
    }
  };

  const handleToggleComplete = async (item: InventoryItem) => {
    try {
      const updatedItem = await inventoryService.updateItem(item.id, {
        ...item,
        is_completed: !item.is_completed
      });
      setItems(items.map(i => i.id === updatedItem.id ? updatedItem : i));
    } catch (err) {
      console.error('Error toggling item:', err);
    }
  };

  const getExpirationStatus = (expirationDate: string) => {
    if (!expirationDate) return null;
    
    const today = new Date();
    const expDate = new Date(expirationDate);
    const diffTime = expDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return { status: 'expired', label: 'Expired', color: 'error' };
    if (diffDays <= 3) return { status: 'warning', label: `${diffDays} days left`, color: 'warning' };
    if (diffDays <= 7) return { status: 'info', label: `${diffDays} days left`, color: 'info' };
    return null;
  };

  const filteredItems = items.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', 'dairy', 'meat', 'produce', 'pantry', 'frozen', 'general'];

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
        Inventory Management
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box display="flex" gap={2} mb={3}>
        <TextField
          placeholder="Search items..."
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
            {categories.map(category => (
              <MenuItem key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenAddDialog(true)}
        >
          Add Item
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        {filteredItems.map((item) => {
          const expirationStatus = getExpirationStatus(item.expiration_date);
          
          return (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6" component="h3">
                      {item.name}
                    </Typography>
                    <Box>
                      {expirationStatus && (
                        <Tooltip title={expirationStatus.label}>
                          <Chip
                            label={expirationStatus.label}
                            color={expirationStatus.color as any}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                        </Tooltip>
                      )}
                      <Chip
                        label={item.category}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {item.quantity} {item.unit} • {item.location}
                  </Typography>
                  
                  {item.expiration_date && (
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Expires: {new Date(item.expiration_date).toLocaleDateString()}
                    </Typography>
                  )}
                  
                  {item.notes && (
                    <Typography variant="body2" color="textSecondary">
                      {item.notes}
                    </Typography>
                  )}
                </CardContent>
                
                <CardActions>
                  <IconButton
                    onClick={() => handleToggleComplete(item)}
                    color={item.is_completed ? "success" : "default"}
                  >
                    <CheckIcon />
                  </IconButton>
                  
                  <IconButton
                    onClick={() => {
                      setEditingItem(item);
                      setOpenEditDialog(true);
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                  
                  <IconButton
                    onClick={() => handleDeleteItem(item.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                  
                  <IconButton
                    onClick={() => console.log('Open barcode scanner')}
                  >
                    <CameraIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      
      {filteredItems.length === 0 && (
        <Box textAlign="center" py={5}>
          <Typography variant="h6" color="textSecondary">
            No items found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Add your first item to get started
          </Typography>
        </Box>
      )}
      
      {/* Add Item Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Item</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newItem.name}
            onChange={(e) => setNewItem({...newItem, name: e.target.value})}
          />
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Category</InputLabel>
            <Select
              value={newItem.category}
              onChange={(e) => setNewItem({...newItem, category: e.target.value as ItemCategory})}
            >
              {categories.slice(1).map(cat => (
                <MenuItem key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Box display="flex" gap={2}>
            <TextField
              margin="dense"
              label="Quantity"
              type="number"
              value={newItem.quantity}
              onChange={(e) => setNewItem({...newItem, quantity: parseInt(e.target.value)})}
            />
            
            <TextField
              margin="dense"
              label="Unit"
              value={newItem.unit}
              onChange={(e) => setNewItem({...newItem, unit: e.target.value})}
            />
          </Box>
          
          <TextField
            margin="dense"
            label="Location"
            fullWidth
            value={newItem.location}
            onChange={(e) => setNewItem({...newItem, location: e.target.value})}
          />
          
          <TextField
            margin="dense"
            label="Expiration Date"
            type="date"
            fullWidth
            value={newItem.expiration_date}
            onChange={(e) => setNewItem({...newItem, expiration_date: e.target.value})}
            InputLabelProps={{
              shrink: true,
            }}
          />
          
          <TextField
            margin="dense"
            label="Notes"
            fullWidth
            multiline
            rows={3}
            value={newItem.notes}
            onChange={(e) => setNewItem({...newItem, notes: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button onClick={handleAddItem} variant="contained">Add Item</Button>
        </DialogActions>
      </Dialog>
      
      {/* Edit Item Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Item</DialogTitle>
        <DialogContent>
          {editingItem && (
            <>
              <TextField
                autoFocus
                margin="dense"
                label="Name"
                fullWidth
                value={editingItem.name}
                onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
              />
              
              <FormControl fullWidth margin="dense">
                <InputLabel>Category</InputLabel>
                <Select
                  value={editingItem.category}
                  onChange={(e) => setEditingItem({...editingItem, category: e.target.value as ItemCategory})}
                >
                  {categories.slice(1).map(cat => (
                    <MenuItem key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <Box display="flex" gap={2}>
                <TextField
                  margin="dense"
                  label="Quantity"
                  type="number"
                  value={editingItem.quantity}
                  onChange={(e) => setEditingItem({...editingItem, quantity: parseInt(e.target.value)})}
                />
                
                <TextField
                  margin="dense"
                  label="Unit"
                  value={editingItem.unit}
                  onChange={(e) => setEditingItem({...editingItem, unit: e.target.value})}
                />
              </Box>
              
              <TextField
                margin="dense"
                label="Location"
                fullWidth
                value={editingItem.location}
                onChange={(e) => setEditingItem({...editingItem, location: e.target.value})}
              />
              
              <TextField
                margin="dense"
                label="Expiration Date"
                type="date"
                fullWidth
                value={editingItem.expiration_date || ''}
                onChange={(e) => setEditingItem({...editingItem, expiration_date: e.target.value})}
                InputLabelProps={{
                  shrink: true,
                }}
              />
              
              <TextField
                margin="dense"
                label="Notes"
                fullWidth
                multiline
                rows={3}
                value={editingItem.notes || ''}
                onChange={(e) => setEditingItem({...editingItem, notes: e.target.value})}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateItem} variant="contained">Save Changes</Button>
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

export default Inventory;