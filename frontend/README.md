# Medical Research Search Frontend

A React-based frontend for the Medical Research Search application that allows users to search across FDA data, clinical trials, and medical news.

## Features

- Modern, responsive UI built with Material-UI
- Real-time search functionality
- Tabbed interface for different data sources:
  - AI-generated summary
  - FDA data (drugs and diseases)
  - Clinical trials
  - Medical news
- Error handling and loading states
- TypeScript for type safety

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

## Development

To start the development server:

```bash
npm start
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## Building for Production

To create a production build:

```bash
npm run build
```

The build output will be in the `build` directory.

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```
REACT_APP_API_BASE_URL=http://localhost:5000
```

## Testing

To run tests:

```bash
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 