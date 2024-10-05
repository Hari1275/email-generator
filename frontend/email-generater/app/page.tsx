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
import { Textarea } from '@/components/ui/textarea';
import React from 'react';

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

  const handleScrapeJobs = async () => {
    try {
      const response = await fetch('http://localhost:8000/scrape_job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      console.log('Scraped job data:', data);
      setJobListings(data);
    } catch (error) {
      console.error('Error scraping jobs:', error);
      // TODO: Add error handling UI
    }
  };

  const handleGenerateEmail = async () => {
    if (!selectedJob) return;
    try {
      const response = await fetch('http://localhost:8000/generate_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: JSON.stringify(selectedJob),
          template_name: emailType,
        }),
      });
      const data = await response.json();
      setGeneratedEmail(data.email);
    } catch (error) {
      console.error('Error generating email:', error);
    }
  };

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
            <Button onClick={handleScrapeJobs}>Scrape Jobs</Button>
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
              <Button onClick={handleGenerateEmail} className='mt-4'>
                Generate Email
              </Button>
            </div>
            {generatedEmail && (
              <div className='mt-4'>
                <h3 className='text-lg font-semibold'>Generated Email:</h3>
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
      )}
    </main>
  );
}
