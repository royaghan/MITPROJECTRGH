import { VercelStaticProps } from '@vercel/static-props';

export const getStaticProps = async () => {
  return {
    props: {},
    staticProps: {
      // Enable static file serving
      staticFiles: true,
      // Add the static files to the build
      dirs: ['templates'],
      // Set the output directory for the static files
      outputDirectory: 'staticfiles_build',
    },
  };
};
