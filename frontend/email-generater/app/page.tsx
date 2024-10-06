'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import React from 'react';
import {
  Loader2,
  Copy,
  Check,
  Search,
  Save,
  Trash2,
  Plus,
  Minus,
} from 'lucide-react';
import copy from 'clipboard-copy';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { motion, AnimatePresence } from 'framer-motion';
interface JobListing {
  Title: string;
  Location: string;
  'Employment Type': string;
  Description: string;
  Experience: string;
  Skills: string;
  Responsibilities: string[];
  Company: string;
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [jobListings, setJobListings] = useState<JobListing[]>([]);
  const [selectedJob, setSelectedJob] = useState<JobListing | null>(null);
  const [generatedEmail, setGeneratedEmail] = useState('');
  const [emailType, setEmailType] = useState('job_application');
  const [isScrapingJobs, setIsScrapingJobs] = useState(false);
  const [isGeneratingEmail, setIsGeneratingEmail] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  // New state variables for customization options
  const [emailTone, setEmailTone] = useState('professional');
  const [emailLength, setEmailLength] = useState('medium');
  const [includePortfolio, setIncludePortfolio] = useState(true);
  const [includeExperiences, setIncludeExperiences] = useState(true);
  const [emphasisPoints, setEmphasisPoints] = useState<string[]>([]);

  // New state for saved jobs
  const [savedJobs, setSavedJobs] = useState<JobListing[]>([]);
  const [jobsToCompare, setJobsToCompare] = useState<JobListing[]>([]);

  const [scrapeError, setScrapeError] = useState<string | null>(null);
  const [emailGenerationError, setEmailGenerationError] = useState<
    string | null
  >(null);

  const handleScrapeJobs = async () => {
    setIsScrapingJobs(true);
    setScrapeError(null);
    try {
      const response = await fetch('http://localhost:9000/scrape_job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Scraped job data:', data);
      setJobListings(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error scraping jobs:', error);
      setScrapeError(
        'Failed to scrape jobs. Please check the URL and try again.'
      );
      setJobListings([]);
    } finally {
      setIsScrapingJobs(false);
    }
  };

  const handleGenerateEmail = async () => {
    if (!selectedJob) return;
    setIsGeneratingEmail(true);
    setEmailGenerationError(null);
    try {
      const response = await fetch('http://localhost:9000/generate_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: JSON.stringify(selectedJob),
          template_name: emailType,
          email_tone: emailTone,
          email_length: emailLength,
          include_portfolio: includePortfolio,
          include_experiences: includeExperiences,
          emphasis_points: emphasisPoints,
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setGeneratedEmail(data.email);
    } catch (error) {
      console.error('Error generating email:', error);
      setEmailGenerationError('Failed to generate email. Please try again.');
      setGeneratedEmail('');
    } finally {
      setIsGeneratingEmail(false);
    }
  };

  const handleCopyEmail = async () => {
    if (generatedEmail) {
      await copy(generatedEmail);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const handleSaveJob = (job: JobListing) => {
    setSavedJobs((prevSavedJobs) => {
      if (!prevSavedJobs.some((savedJob) => savedJob.Title === job.Title)) {
        return [...prevSavedJobs, job];
      }
      return prevSavedJobs;
    });
  };

  const handleRemoveSavedJob = (job: JobListing) => {
    setSavedJobs((prevSavedJobs) =>
      prevSavedJobs.filter((savedJob) => savedJob.Title !== job.Title)
    );
  };

  const addToComparison = (job: JobListing) => {
    if (jobsToCompare.length < 2) {
      setJobsToCompare([...jobsToCompare, job]);
    }
  };

  const removeFromComparison = (job: JobListing) => {
    setJobsToCompare(jobsToCompare.filter((j) => j.Title !== job.Title));
  };

  const CustomizationOptions = () => (
    <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
      <CardHeader>
        <CardTitle className='text-3xl font-bold text-gray-900'>
          Email Customization
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className='space-y-6'>
          <div className='grid grid-cols-2 gap-4'>
            <div>
              <label className='block text-sm font-medium text-gray-700 mb-1'>
                Tone:
              </label>
              <Select value={emailTone} onValueChange={setEmailTone}>
                <SelectTrigger className='w-full'>
                  <SelectValue placeholder='Select tone' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='professional'>Professional</SelectItem>
                  <SelectItem value='friendly'>Friendly</SelectItem>
                  <SelectItem value='enthusiastic'>Enthusiastic</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className='block text-sm font-medium text-gray-700 mb-1'>
                Length:
              </label>
              <Select value={emailLength} onValueChange={setEmailLength}>
                <SelectTrigger className='w-full'>
                  <SelectValue placeholder='Select length' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='short'>Short</SelectItem>
                  <SelectItem value='medium'>Medium</SelectItem>
                  <SelectItem value='long'>Long</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className='flex space-x-4'>
            <label className='flex items-center space-x-2 cursor-pointer'>
              <input
                type='checkbox'
                checked={includePortfolio}
                onChange={(e) => setIncludePortfolio(e.target.checked)}
                className='form-checkbox h-5 w-5 text-blue-600'
              />
              <span className='text-gray-700'>Include Portfolio Links</span>
            </label>
            <label className='flex items-center space-x-2 cursor-pointer'>
              <input
                type='checkbox'
                checked={includeExperiences}
                onChange={(e) => setIncludeExperiences(e.target.checked)}
                className='form-checkbox h-5 w-5 text-blue-600'
              />
              <span className='text-gray-700'>
                Include Specific Experiences
              </span>
            </label>
          </div>
          <div>
            <label className='block text-sm font-medium text-gray-700 mb-1'>
              Emphasis Points:
            </label>
            <Input
              placeholder='Enter emphasis points (comma-separated)'
              value={emphasisPoints.join(', ')}
              onChange={(e) =>
                setEmphasisPoints(
                  e.target.value.split(',').map((point) => point.trim())
                )
              }
              className='w-full'
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const SavedJobsTab = () => (
    <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
      <CardHeader>
        <CardTitle className='text-3xl font-bold text-gray-900'>
          Saved Job Listings
        </CardTitle>
      </CardHeader>
      <CardContent>
        {savedJobs.length === 0 ? (
          <p className='text-gray-600'>No saved jobs yet.</p>
        ) : (
          <ul className='space-y-3'>
            {savedJobs.map((job, index) => (
              <motion.li
                key={index}
                className='flex justify-between items-center bg-white p-3 rounded-lg shadow'
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.3 }}
              >
                <Button
                  variant='ghost'
                  onClick={() => setSelectedJob(job)}
                  className='text-left text-gray-800'
                >
                  <span className='font-medium'>{job.Title}</span>
                  <span className='text-sm text-gray-500 block'>
                    {job.Company}
                  </span>
                </Button>
                <Button
                  variant='ghost'
                  size='icon'
                  onClick={() => handleRemoveSavedJob(job)}
                  className='text-red-500 hover:text-red-700'
                >
                  <Trash2 className='h-5 w-5' />
                </Button>
              </motion.li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );

  const JobComparison = () => (
    <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
      <CardHeader>
        <CardTitle className='text-3xl font-bold text-gray-900'>
          Job Comparison
        </CardTitle>
      </CardHeader>
      <CardContent>
        {jobsToCompare.length === 0 ? (
          <p className='text-gray-600'>Select jobs to compare (max 2)</p>
        ) : (
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            {jobsToCompare.map((job, index) => (
              <motion.div
                key={index}
                className='bg-white p-4 rounded-lg shadow'
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className='font-bold text-lg text-gray-800 mb-2'>
                  {job.Title}
                </h3>
                <p className='text-gray-700'>
                  <strong>Company:</strong> {job.Company}
                </p>
                <p className='text-gray-700'>
                  <strong>Location:</strong> {job.Location}
                </p>
                <p className='text-gray-700'>
                  <strong>Employment Type:</strong> {job['Employment Type']}
                </p>
                <Button
                  variant='ghost'
                  size='sm'
                  onClick={() => removeFromComparison(job)}
                  className='mt-3 text-red-500 hover:text-red-700'
                >
                  <Minus className='h-4 w-4 mr-1' />
                  Remove
                </Button>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <main className='min-h-screen bg-white p-8'>
      <div className='max-w-7xl mx-auto'>
        <h1 className='text-5xl font-extrabold text-center mb-12 text-gray-900 drop-shadow-lg'>
          AI-Powered Cold Email Generator
        </h1>

        <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
          <CardHeader>
            <CardTitle className='text-3xl font-bold text-gray-900'>
              Job Scraper
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='flex space-x-2'>
              <Input
                type='text'
                placeholder="Enter company's career page URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className='flex-grow bg-white bg-opacity-50 border-gray-300 text-gray-800 placeholder-gray-500'
              />
              <Button
                onClick={handleScrapeJobs}
                disabled={isScrapingJobs || !url.trim()}
                className='bg-blue-600 hover:bg-blue-700 text-white'
              >
                {isScrapingJobs ? (
                  <>
                    <Loader2 className='mr-2 h-5 w-5 animate-spin' />
                    Scraping...
                  </>
                ) : (
                  <>
                    <Search className='mr-2 h-5 w-5' />
                    Scrape Jobs
                  </>
                )}
              </Button>
            </div>
            {scrapeError && <p className='text-red-600 mt-2'>{scrapeError}</p>}
          </CardContent>
        </Card>

        <Tabs defaultValue='jobListings' className='mb-8'>
          <TabsList className='bg-gray-100 rounded-xl p-1'>
            <TabsTrigger
              value='jobListings'
              className='px-4 py-2 text-gray-900'
            >
              Job Listings
            </TabsTrigger>
            <TabsTrigger value='savedJobs' className='px-4 py-2 text-gray-900'>
              Saved Jobs
            </TabsTrigger>
          </TabsList>
          <TabsContent value='jobListings'>
            <AnimatePresence>
              {jobListings.length > 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
                    <CardHeader>
                      <CardTitle className='text-3xl font-bold text-gray-900'>
                        Job Listings
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className='space-y-3'>
                        {jobListings.map((job, index) => (
                          <li
                            key={index}
                            className='flex justify-between items-center bg-white p-4 rounded-lg shadow-sm'
                          >
                            {job.Title !== 'Not specified' ? (
                              <>
                                <Button
                                  variant='ghost'
                                  onClick={() => setSelectedJob(job)}
                                  className='text-left flex-grow mr-2 text-gray-800 hover:bg-gray-200'
                                >
                                  <span className='font-medium'>
                                    {job.Title}
                                  </span>
                                </Button>
                                <Button
                                  variant='ghost'
                                  size='icon'
                                  onClick={() => handleSaveJob(job)}
                                  className='text-white hover:bg-white hover:bg-opacity-10'
                                >
                                  <Save className='h-5 w-5' />
                                </Button>
                              </>
                            ) : (
                              <p className='text-yellow-300'>
                                Unable to retrieve job details
                              </p>
                            )}
                          </li>
                        ))}
                      </ul>
                      {jobListings.some(
                        (job) => job.Title === 'Not specified'
                      ) && (
                        <p className='text-yellow-300 mt-4'>
                          Some job details couldn't be retrieved. Please ensure
                          you're providing a direct link to a job details page.
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
                    <CardContent>
                      <p className='text-gray-900 text-center py-4'>
                        No job listings found. Please provide a URL that links
                        directly to a job details page.
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
          </TabsContent>
          <TabsContent value='savedJobs'>
            <SavedJobsTab />
          </TabsContent>
        </Tabs>

        <JobComparison />

        {selectedJob && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
              <CardHeader>
                <CardTitle className='text-3xl font-bold text-gray-900'>
                  {selectedJob.Title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className='space-y-3 text-gray-900'>
                  <p>
                    <strong>Company:</strong> {selectedJob.Company}
                  </p>
                  <p>
                    <strong>Location:</strong> {selectedJob.Location}
                  </p>
                  <p>
                    <strong>Employment Type:</strong>{' '}
                    {selectedJob['Employment Type']}
                  </p>
                  <p>
                    <strong>Experience:</strong> {selectedJob.Experience}
                  </p>
                  <p>
                    <strong>Skills:</strong> {selectedJob.Skills}
                  </p>
                  <p>
                    <strong>Description:</strong> {selectedJob.Description}
                  </p>
                  <div>
                    <strong>Responsibilities:</strong>
                    <ul className='list-disc pl-5 mt-2 space-y-1'>
                      {selectedJob.Responsibilities.map((resp, index) => (
                        <li key={index}>{resp}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                <Button
                  variant='outline'
                  size='sm'
                  onClick={() => addToComparison(selectedJob)}
                  disabled={jobsToCompare.length >= 2}
                  className='mt-4 text-white border-white border-opacity-50 hover:bg-white hover:bg-opacity-10'
                >
                  <Plus className='h-4 w-4 mr-1' />
                  Add to Comparison
                </Button>
              </CardContent>
            </Card>

            <CustomizationOptions />

            <Card className='mb-8 bg-gray-50 shadow-lg rounded-xl'>
              <CardHeader>
                <CardTitle className='text-3xl font-bold text-gray-900'>
                  Generate Email for: {selectedJob.Title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className='space-y-4'>
                  <Select
                    value={emailType}
                    onValueChange={(value) => setEmailType(value)}
                  >
                    <SelectTrigger className='w-full bg-white bg-opacity-50 border-gray-300 text-gray-800'>
                      <SelectValue placeholder='Select email type' />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value='job_application'>
                        Job Application
                      </SelectItem>
                      <SelectItem value='business_outreach'>
                        Business Outreach
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={handleGenerateEmail}
                    disabled={isGeneratingEmail}
                    className='w-full bg-blue-600 hover:bg-blue-700 text-white'
                  >
                    {isGeneratingEmail ? (
                      <>
                        <Loader2 className='mr-2 h-5 w-5 animate-spin' />
                        Generating Email...
                      </>
                    ) : (
                      <>
                        <span className='mr-2'>✉️</span>
                        Generate Email
                      </>
                    )}
                  </Button>
                  {emailGenerationError && (
                    <p className='text-red-600 mt-2'>{emailGenerationError}</p>
                  )}
                </div>
                {generatedEmail && (
                  <motion.div
                    className='mt-6'
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className='flex justify-between items-center mb-2'>
                      <h3 className='text-xl font-semibold text-gray-900'>
                        Generated Email:
                      </h3>
                      <Button
                        onClick={handleCopyEmail}
                        variant='outline'
                        size='sm'
                        className='text-black border-white border-opacity-50 hover:bg-white hover:bg-opacity-10'
                      >
                        {isCopied ? (
                          <>
                            <Check className='mr-2 h-4 w-4' />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className='mr-2 h-4 w-4' />
                            Copy
                          </>
                        )}
                      </Button>
                    </div>
                    <div className='bg-white p-4 rounded-lg shadow-inner mt-2 whitespace-pre-wrap font-mono text-sm overflow-auto max-h-96 text-gray-900'>
                      {generatedEmail.split('\n').map((line, index) => (
                        <React.Fragment key={index}>
                          {line}
                          <br />
                        </React.Fragment>
                      ))}
                    </div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </main>
  );
}
