import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import type { Division, Department, SubDepartment } from '../../types';

type User = {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  division_id?: number;
  department_id?: number;
  subdepartment_id?: number;
};

const UserRole = {
  ADMIN: 'ADMIN',
  DIVISION_MANAGER: 'DIVISION_MANAGER',
  DEPARTMENT_HEAD: 'DEPARTMENT_HEAD',
  SUB_DEPARTMENT_STAFF: 'SUB_DEPARTMENT_STAFF',
};

export default function UserManagement() {
  const { user, token } = useAuth();
  const navigate = useNavigate();

  // Main state
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [userToDelete, setUserToDelete] = useState<number | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Organizational data
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [subdepartments, setSubdepartments] = useState<SubDepartment[]>([]);

  // Custom creation modals
  const [showDivModal, setShowDivModal] = useState(false);
  const [showDeptModal, setShowDeptModal] = useState(false);
  const [showSubdeptModal, setShowSubdeptModal] = useState(false);
  const [newDivName, setNewDivName] = useState('');
  const [newDivType, setNewDivType] = useState('SUPPORT');
  const [newDeptName, setNewDeptName] = useState('');
  const [newSubdeptName, setNewSubdeptName] = useState('');
  const [selectedDivisionForDept, setSelectedDivisionForDept] = useState<number | null>(null);
  const [selectedDeptForSubdept, setSelectedDeptForSubdept] = useState<number | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'SUB_DEPARTMENT_STAFF',
    is_active: true,
    division_id: '',
    department_id: '',
    subdepartment_id: '',
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!user || user.role !== 'ADMIN') {
      navigate('/');
      return;
    }
    fetchUsers();
    fetchOrganizationalData();
  }, [user, token]);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Fetch organizational structure
  const fetchOrganizationalData = async () => {
    if (!token) return;
    try {
      const [divisionsData, departmentsData] = await Promise.all([
        api.getDivisions(token),
        api.getDepartments(token)
      ]);
      setDivisions(divisionsData);
      setDepartments(departmentsData);
    } catch (err) {
      console.error('Failed to fetch organizational data:', err);
    }
  };

  // Fetch subdepartments when department selected
  const fetchSubdepartments = async (departmentId: number) => {
    if (!token) return;
    try {
      const data = await api.getSubDepartments(token, departmentId);
      setSubdepartments(data);
    } catch (err) {
      console.error('Failed to fetch subdepartments:', err);
      setSubdepartments([]);
    }
  };

  // Handle division change
  const handleDivisionChange = (divisionId: string) => {
    setFormData({
      ...formData,
      division_id: divisionId,
      department_id: '',
      subdepartment_id: ''
    });
    setSubdepartments([]);
  };

  // Handle department change  
  const handleDepartmentChange = (departmentId: string) => {
    setFormData({
      ...formData,
      department_id: departmentId,
      subdepartment_id: ''
    });
    if (departmentId) {
      fetchSubdepartments(parseInt(departmentId));
    } else {
      setSubdepartments([]);
    }
  };

  // Get filtered departments based on selected division
  const filteredDepartments = formData.division_id
    ? departments.filter(d => d.division_id === parseInt(formData.division_id))
    : [];

  const fetchUsers = async () => {
    if (!token) return;
    try {
      const data = await api.getUsers(token);
      setUsers(data);
    } catch (err) {
      console.error('Failed to load users:', err);
      showNotification('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
  };

  const handleOpenModal = (u: User | null = null) => {
    if (u) {
      setEditingUser(u);
      setFormData({
        username: u.username,
        email: u.email,
        full_name: u.full_name,
        password: '',
        role: u.role,
        is_active: u.is_active,
        division_id: u.division_id?.toString() || '',
        department_id: u.department_id?.toString() || '',
        subdepartment_id: u.subdepartment_id?.toString() || '',
      });
      if (u.department_id) {
        fetchSubdepartments(u.department_id);
      }
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'SUB_DEPARTMENT_STAFF',
        is_active: true,
        division_id: '',
        department_id: '',
        subdepartment_id: '',
      });
      setSubdepartments([]);
    }
    setFormErrors({});
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingUser(null);
    setFormErrors({});
    setSubdepartments([]);
  };

  // Custom division creation
  const handleCreateDivision = async () => {
    if (!newDivName || !token) return;
    try {
      await api.createDivision(token, {
        name: newDivName,
        type: newDivType,
        description: newDivName
      });
      await fetchOrganizationalData();
      setNewDivName('');
      setNewDivType('SUPPORT');
      setShowDivModal(false);
      showNotification('Division created successfully', 'success');
    } catch (err: any) {
      showNotification(err?.response?.data?.detail || 'Failed to create division', 'error');
    }
  };

  // Custom department creation
  const handleCreateDepartment = async () => {
    if (!newDeptName || !selectedDivisionForDept || !token) return;
    try {
      await api.createDepartment(token, {
        name: newDeptName,
        division_id: selectedDivisionForDept
      });
      await fetchOrganizationalData();
      setNewDeptName('');
      setSelectedDivisionForDept(null);
      setShowDeptModal(false);
      showNotification('Department created successfully', 'success');
    } catch (err: any) {
      showNotification(err?.response?.data?.detail || 'Failed to create department', 'error');
    }
  };

  // Custom subdepartment creation
  const handleCreateSubdepartment = async () => {
    if (!newSubdeptName || !selectedDeptForSubdept || !token) return;
    try {
      await api.createSubDepartment(token, selectedDeptForSubdept, {
        name: newSubdeptName
      });
      if (formData.department_id) {
        await fetchSubdepartments(parseInt(formData.department_id));
      }
      setNewSubdeptName('');
      setSelectedDeptForSubdept(null);
      setShowSubdeptModal(false);
      showNotification('Sub-department created successfully', 'success');
    } catch (err: any) {
      showNotification(err?.response?.data?.detail || 'Failed to create sub-department', 'error');
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.username) errors.username = 'Username is required';
    if (!formData.email) errors.email = 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) errors.email = 'Invalid email format';
    if (!formData.full_name) errors.full_name = 'Full name is required';
    if (!editingUser && !formData.password) errors.password = 'Password is required';
    if (formData.password && formData.password.length < 8) errors.password = 'Password must be at least 8 characters';
    if (!formData.role) errors.role = 'Role is required';

    // Dynamic Hierarchy Validation
    if (formData.role !== 'ADMIN') {
      if (!formData.division_id) errors.division_id = 'Division is required';

      if (['DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'].includes(formData.role)) {
        if (!formData.department_id) errors.department_id = 'Department is required';
      }

      if (formData.role === 'SUB_DEPARTMENT_STAFF') {
        if (!formData.subdepartment_id) errors.subdepartment_id = 'Sub-Department is required';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm() || !token) return;

    try {
      const userData: any = {
        username: formData.username,
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        is_active: formData.is_active,
        division_id: formData.division_id ? parseInt(formData.division_id) : null,
        department_id: formData.department_id ? parseInt(formData.department_id) : null,
        subdepartment_id: formData.subdepartment_id ? parseInt(formData.subdepartment_id) : null,
      };

      if (formData.password) {
        userData.password = formData.password;
      }

      if (editingUser) {
        const data = await api.updateUser(token, editingUser.id, userData);
        setUsers(users.map(u => u.id === editingUser.id ? data : u));
        showNotification('User updated successfully', 'success');
      } else {
        const data = await api.createUser(token, userData);
        setUsers([...users, data]);
        showNotification('User created successfully', 'success');
      }
      handleCloseModal();
    } catch (err: any) {
      console.error(err);
      showNotification(err?.response?.data?.detail || 'Save failed', 'error');
    }
  };

  const handleDeleteClick = (id: number) => {
    setUserToDelete(id);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!userToDelete || !token) return;
    try {
      await api.deleteUser(token, userToDelete);
      setUsers(users.filter(u => u.id !== userToDelete));
      showNotification('User deleted successfully', 'success');
    } catch (err: any) {
      console.error(err);
      showNotification(err?.response?.data?.detail || 'Delete failed', 'error');
    } finally {
      setShowDeleteModal(false);
      setUserToDelete(null);
    }
  };

  if (!user || user.role !== 'ADMIN') {
    return (
      <div className="container" style={{ padding: '3rem', textAlign: 'center' }}>
        <h2>Access Denied</h2>
        <p>You don't have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div>
      {notification && (
        <div
          style={{
            position: 'fixed',
            top: '2rem',
            right: '2rem',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            background: notification.type === 'success' ? 'var(--success)' : 'var(--error)',
            color: 'white',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 9999,
          }}
        >
          {notification.message}
        </div>
      )}

      <div className="card-header">
        <div>
          <h1 className="card-title">User Management</h1>
          <p className="text-muted">{users.length} users in system</p>
        </div>
        <button className="btn btn-primary" onClick={() => handleOpenModal()}>
          + Add User
        </button>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <div className="spinner"></div>
          </div>
        ) : (
          <table className="data-table compact-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>
                    No users found
                  </td>
                </tr>
              ) : (
                users.map(u => (
                  <tr key={u.id}>
                    <td><strong>{u.full_name}</strong></td>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td>
                      <span className="badge badge-info" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        {u.role.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-success' : 'badge-error'}`} style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => handleOpenModal(u)}
                        style={{ marginRight: '0.5rem' }}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => handleDeleteClick(u.id)}
                        disabled={u.id === user?.id}
                        style={{
                          color: 'var(--error)',
                          borderColor: 'var(--error)',
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      <style>{`
        .compact-table th,
        .compact-table td {
          padding: 0.5rem 0.75rem !important;
          font-size: 0.9rem;
        }
        
        .compact-table th {
          font-weight: 600;
          background: #f8f9fa;
          text-transform: uppercase;
          font-size: 0.75rem;
          letter-spacing: 0.05em;
        }

        .btn-sm {
          padding: 0.25rem 0.5rem !important;
          font-size: 0.8rem !important;
          line-height: 1.2;
        }
      `}</style>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="card-header" style={{ marginBottom: '1.5rem' }}>
              <h2 className="card-title">{editingUser ? 'Edit User' : 'Add New User'}</h2>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Full Name *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  />
                  {formErrors.full_name && (
                    <small style={{ color: 'var(--error)' }}>{formErrors.full_name}</small>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Username *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    disabled={!!editingUser}
                  />
                  {formErrors.username && (
                    <small style={{ color: 'var(--error)' }}>{formErrors.username}</small>
                  )}
                </div>
              </div>

              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Email *</label>
                  <input
                    type="email"
                    className="form-input"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                  {formErrors.email && (
                    <small style={{ color: 'var(--error)' }}>{formErrors.email}</small>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">
                    {editingUser ? 'New Password (blank = no change)' : 'Password *'}
                  </label>
                  <input
                    type="password"
                    className="form-input"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  />
                  {formErrors.password && (
                    <small style={{ color: 'var(--error)' }}>{formErrors.password}</small>
                  )}
                </div>
              </div>

              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Role *</label>
                  <select
                    className="form-select"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  >
                    {Object.values(UserRole).map((value) => (
                      <option key={value} value={value}>
                        {value.replace(/_/g, ' ')}
                      </option>
                    ))}
                  </select>
                  {formErrors.role && (
                    <small style={{ color: 'var(--error)' }}>{formErrors.role}</small>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Active Status</label>
                  <select
                    className="form-select"
                    value={formData.is_active ? 'true' : 'false'}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.value === 'true' })}
                  >
                    <option value="true">Active</option>
                    <option value="false">Inactive</option>
                  </select>
                </div>
              </div>

              {/* Cascading Organizational Dropdowns */}
              <div className="form-group">
                <label className="form-label">
                  Division {formData.role !== 'ADMIN' && '*'}
                </label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    className="form-select"
                    style={{ flex: 1 }}
                    value={formData.division_id}
                    onChange={(e) => handleDivisionChange(e.target.value)}
                  >
                    <option value="">-- Select Division --</option>
                    {divisions.map(div => (
                      <option key={div.id} value={div.id}>{div.name}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => setShowDivModal(true)}
                    className="btn btn-outline"
                    title="Add New Division"
                  >
                    + New
                  </button>
                </div>
                {formErrors.division_id && (
                  <small style={{ color: 'var(--error)' }}>{formErrors.division_id}</small>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">
                  Department {['DEPARTMENT_HEAD', 'SUB_DEPARTMENT_STAFF'].includes(formData.role) && '*'}
                </label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    className="form-select"
                    style={{ flex: 1 }}
                    value={formData.department_id}
                    onChange={(e) => handleDepartmentChange(e.target.value)}
                    disabled={!formData.division_id}
                  >
                    <option value="">-- Select Department --</option>
                    {filteredDepartments.map(dept => (
                      <option key={dept.id} value={dept.id}>{dept.name}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => {
                      if (formData.division_id) {
                        setSelectedDivisionForDept(parseInt(formData.division_id));
                        setShowDeptModal(true);
                      }
                    }}
                    disabled={!formData.division_id}
                    className="btn btn-outline"
                    title="Add New Department"
                  >
                    + New
                  </button>
                </div>

                {formErrors.department_id && (
                  <small style={{ color: 'var(--error)' }}>{formErrors.department_id}</small>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">
                  Sub-Department {formData.role === 'SUB_DEPARTMENT_STAFF' && '*'}
                </label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    className="form-select"
                    style={{ flex: 1 }}
                    value={formData.subdepartment_id}
                    onChange={(e) => setFormData({ ...formData, subdepartment_id: e.target.value })}
                    disabled={!formData.department_id}
                  >
                    <option value="">-- Select Sub-Department --</option>
                    {subdepartments.map(subdept => (
                      <option key={subdept.id} value={subdept.id}>{subdept.name}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => {
                      if (formData.department_id) {
                        setSelectedDeptForSubdept(parseInt(formData.department_id));
                        setShowSubdeptModal(true);
                      }
                    }}
                    disabled={!formData.department_id}
                    className="btn btn-outline"
                    title="Add New Sub-Department"
                  >
                    + New
                  </button>
                </div>

                {formErrors.subdepartment_id && (
                  <small style={{ color: 'var(--error)' }}>{formErrors.subdepartment_id}</small>
                )}
              </div>

              <div className="flex gap-md" style={{ marginTop: '2rem' }}>
                <button type="submit" className="btn btn-primary">
                  {editingUser ? 'Update User' : 'Create User'}
                </button>
                <button type="button" className="btn btn-outline" onClick={handleCloseModal}>
                  Cancel
                </button>
              </div>
            </form>
          </div >
        </div >
      )
      }

      {/* New Division Modal */}
      {
        showDivModal && (
          <div className="modal-overlay" onClick={() => setShowDivModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '450px' }}>
              <div className="card-header" style={{ marginBottom: '1rem' }}>
                <h2 className="card-title">➕ Add New Division</h2>
              </div>
              <div className="form-group">
                <label className="form-label">Division Name *</label>
                <input
                  type="text"
                  className="form-input"
                  value={newDivName}
                  onChange={(e) => setNewDivName(e.target.value)}
                  placeholder="Enter division name"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label">Type *</label>
                <select
                  className="form-select"
                  value={newDivType}
                  onChange={(e) => setNewDivType(e.target.value)}
                >
                  <option value="SUPPORT">Support</option>
                  <option value="INCOME_GENERATING">Income Generating</option>
                </select>
              </div>
              <div className="flex gap-md" style={{ marginTop: '1.5rem' }}>
                <button
                  className="btn btn-primary"
                  onClick={handleCreateDivision}
                  disabled={!newDivName.trim()}
                >
                  Create Division
                </button>
                <button className="btn btn-outline" onClick={() => setShowDivModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* New Department Modal */}
      {
        showDeptModal && (
          <div className="modal-overlay" onClick={() => setShowDeptModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '450px' }}>
              <div className="card-header" style={{ marginBottom: '1rem' }}>
                <h2 className="card-title">➕ Add New Department</h2>
              </div>
              <div className="form-group">
                <label className="form-label">Department Name *</label>
                <input
                  type="text"
                  className="form-input"
                  value={newDeptName}
                  onChange={(e) => setNewDeptName(e.target.value)}
                  placeholder="Enter department name"
                  autoFocus
                />
              </div>
              <div className="flex gap-md" style={{ marginTop: '1.5rem' }}>
                <button
                  className="btn btn-primary"
                  onClick={handleCreateDepartment}
                  disabled={!newDeptName.trim()}
                >
                  Create Department
                </button>
                <button className="btn btn-outline" onClick={() => setShowDeptModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* New Sub-Department Modal */}
      {
        showSubdeptModal && (
          <div className="modal-overlay" onClick={() => setShowSubdeptModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '450px' }}>
              <div className="card-header" style={{ marginBottom: '1rem' }}>
                <h2 className="card-title">➕ Add New Sub-Department</h2>
              </div>
              <div className="form-group">
                <label className="form-label">Sub-Department Name *</label>
                <input
                  type="text"
                  className="form-input"
                  value={newSubdeptName}
                  onChange={(e) => setNewSubdeptName(e.target.value)}
                  placeholder="Enter sub-department name"
                  autoFocus
                />
              </div>
              <div className="flex gap-md" style={{ marginTop: '1.5rem' }}>
                <button
                  className="btn btn-primary"
                  onClick={handleCreateSubdepartment}
                  disabled={!newSubdeptName.trim()}
                >
                  Create Sub-Department
                </button>
                <button className="btn btn-outline" onClick={() => setShowSubdeptModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )
      }

      {/* Delete Confirmation Modal */}
      {
        showDeleteModal && (
          <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '450px' }}>
              <div className="card-header" style={{ marginBottom: '1rem' }}>
                <h2 className="card-title">Confirm Delete</h2>
              </div>
              <p style={{ marginBottom: '2rem' }}>
                Are you sure you want to delete this user? This action cannot be undone.
              </p>
              <div className="flex gap-md">
                <button
                  className="btn btn-outline"
                  onClick={handleConfirmDelete}
                  style={{ color: 'var(--error)', borderColor: 'var(--error)' }}
                >
                  Delete User
                </button>
                <button className="btn btn-outline" onClick={() => setShowDeleteModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )
      }
    </div >
  );
}
