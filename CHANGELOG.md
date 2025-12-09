# Changelog

All notable changes to the Tebita SLA System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-rc.1] - 2025-12-08

Release Candidate 1 - Pre-deployment testing version

### Added
- Cross-division request capabilities for Division Managers
- Division Managers can send and receive requests from other divisions
- Comprehensive permission system for viewing requests across organizational hierarchy
- Division, department, and subdepartment access levels in request view endpoint
- Status filtering for incoming requests (PENDING and IN_PROGRESS only)
- Notification count accuracy improvements
- Optional department/subdepartment fields in new request form
- Semantic versioning implementation (SemVer)
- VERSION file for version tracking
- Version display in application config

### Changed
- Request form validation: department and subdepartment now optional (only division required)
- Incoming requests now only show PENDING and IN_PROGRESS statuses
- Notification badge count now matches actual incoming requests count
- Self-request validation improved to handle optional department fields correctly
- Permission checks updated to support users without department assignments (Division Managers)

### Fixed
- Division Managers can now successfully create requests (removed department requirement)
- Cross-division requests now appear in recipient's incoming requests
- Request detail view now accessible to Division Managers
- "Request not found" error when Division Managers try to view requests
- Notification count mismatch with actual visible incoming requests
- Self-request validation no longer blocks valid cross-division requests
- Request view permissions now check all hierarchy levels (division/department/subdepartment)

### Security
- Enhanced request viewing permissions with comprehensive hierarchy checks
- Role-based access control strengthened across all endpoints
- Proper validation of organizational hierarchy in request creation

---

## [1.0.0-beta.1] - 2025-11-xx

Beta Release - Feature-complete testing version

### Added
- Complete request management system
- Role-based dashboards (Admin, Division Manager, Department Head, Staff)
- SLA monitoring and compliance tracking
- M&E Dashboard with analytics
- KPI tracking and scorecard system
- Department ratings and satisfaction tracking
- Real-time notifications
- File attachment support
- Request workflow management
- User management with role assignment
- Division/Department/SubDepartment organizational structure

### Changed
- Database optimized for production workload
- UI/UX refinements based on QA feedback
- Performance improvements for large datasets

### Fixed
- Various bug fixes from alpha testing
- Data consistency improvements
- Error handling enhancements

---

## [0.1.0-alpha.1] - 2025-10-xx

Alpha Release - Initial development version

### Added
- Initial project setup
- Basic request creation and tracking
- User authentication and authorization
- Database schema design
- Frontend application structure
- Backend API endpoints
- Development environment configuration

---

## Version Naming Convention

- **alpha** - Early development, unstable
- **beta** - Feature-complete, testing phase
- **rc** (Release Candidate) - Pre-production, final testing
- **stable** - Production release

## Upcoming

See [VERSIONING_GUIDE.md](VERSIONING_GUIDE.md) for version management practices.

For the roadmap to v1.0.0 stable, see project documentation.
