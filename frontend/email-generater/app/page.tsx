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
import { Loader2, Copy, Check } from 'lucide-react';
import copy from 'clipboard-copy';

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

  const handleScrapeJobs = async () => {
    setIsScrapingJobs(true);
    try {
      const response = await fetch('http://localhost:8000/scrape_job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      console.log('Scraped job data:', data);
      setJobListings(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error scraping jobs:', error);
      setJobListings([]);
    } finally {
      setIsScrapingJobs(false);
    }
  };

  const handleGenerateEmail = async () => {
    if (!selectedJob) return;
    setIsGeneratingEmail(true);
    try {
      const response = await fetch('http://localhost:8000/generate_email', {
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

  const CustomizationOptions = () => (
    <Card className='mb-4'>
      <CardHeader>
        <CardTitle>Email Customization Options</CardTitle>
      </CardHeader>
      <CardContent>
        <div className='space-y-4'>
          <div>
            <label>Tone:</label>
            <Select value={emailTone} onValueChange={setEmailTone}>
              <SelectTrigger>
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
            <label>Length:</label>
            <Select value={emailLength} onValueChange={setEmailLength}>
              <SelectTrigger>
                <SelectValue placeholder='Select length' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='short'>Short</SelectItem>
                <SelectItem value='medium'>Medium</SelectItem>
                <SelectItem value='long'>Long</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label>
              <input
                type='checkbox'
                checked={includePortfolio}
                onChange={(e) => setIncludePortfolio(e.target.checked)}
              />
              Include Portfolio Links
            </label>
          </div>
          <div>
            <label>
              <input
                type='checkbox'
                checked={includeExperiences}
                onChange={(e) => setIncludeExperiences(e.target.checked)}
              />
              Include Specific Experiences
            </label>
          </div>
          <div>
            <label>Emphasis Points:</label>
            <Input
              placeholder='Enter emphasis points (comma-separated)'
              value={emphasisPoints.join(', ')}
              onChange={(e) =>
                setEmphasisPoints(
                  e.target.value.split(',').map((point) => point.trim())
                )
              }
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <main className='container mx-auto p-4'>
      <h1 className='text-3xl font-bold mb-4'>Cold Email Generator SaaS</h1>

      <Card className='mb-4'>
        <CardHeader>
          <CardTitle>Job Scraper</CardTitle>
        </CardHeader>
        <CardContent>
          <div className='flex space-x-2'>
            <Input
              type='text'
              placeholder="Enter company's career page URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <Button onClick={handleScrapeJobs} disabled={isScrapingJobs}>
              {isScrapingJobs ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Scraping...
                </>
              ) : (
                'Scrape Jobs'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {jobListings.length > 0 && (
        <Card className='mb-4'>
          <CardHeader>
            <CardTitle>Job Listings</CardTitle>
          </CardHeader>
          <CardContent>
            <ul>
              {jobListings.map((job, index) => (
                <li key={index} className='mb-2'>
                  <Button variant='outline' onClick={() => setSelectedJob(job)}>
                    {job.Title}
                  </Button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {selectedJob && (
        <>
          <Card className='mb-4'>
            <CardHeader>
              <CardTitle>{selectedJob.Title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className='space-y-2'>
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
                  <ul className='list-disc pl-5 mt-2'>
                    {selectedJob.Responsibilities.map((resp, index) => (
                      <li key={index}>{resp}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
          <CustomizationOptions />
          <Card>
            <CardHeader>
              <CardTitle>Generate Email for: {selectedJob.Title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                <Select
                  value={emailType}
                  onValueChange={(value) => setEmailType(value)}
                >
                  <SelectTrigger className='w-full'>
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
                  className='mt-4'
                >
                  {isGeneratingEmail ? (
                    <>
                      <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                      Generating Email...
                    </>
                  ) : (
                    'Generate Email'
                  )}
                </Button>
              </div>
              {generatedEmail && (
                <div className='mt-4'>
                  <div className='flex justify-between items-center'>
                    <h3 className='text-lg font-semibold'>Generated Email:</h3>
                    <Button
                      onClick={handleCopyEmail}
                      variant='outline'
                      size='sm'
                      className='ml-2'
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
                  <div className='bg-gray-100 p-4 rounded mt-2 whitespace-pre-wrap font-mono text-sm'>
                    {generatedEmail.split('\n').map((line, index) => (
                      <React.Fragment key={index}>
                        {line}
                        <br />
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </main>
  );
}
