---
title: "FSF is working on freedom in machine learning applications"
type: source
tags: [FSF, free-software, training-data, open-source-ai]
published: 2024-10-22
scraped: 2026-09-23
source_file: raw/NewsScrap/FSF is working on freedom in machine learning applications.md
source_url: "https://www.fsf.org/news/fsf-is-working-on-freedom-in-machine-learning-applications"
last_updated: 2026-09-23
---

## Summary

In an October 22, 2024 press release, the [[FreeSoftwareFoundation]] announced that a working group of its board members, staff, and management is drafting a statement of criteria for when a machine-learning application is free. According to the FSF, such an application is free only if its software, its raw [[TrainingData]], and the scripts that process that data all grant users the four freedoms, and the release may also need to include the model parameters under terms that permit use and redistribution. The FSF describes applications that fall short as nonfree by definition, while allowing that using some of them could be ethically excusable when data such as personal medical records cannot be released. The release is the FSF's own statement; external assessment of the criteria is outside the raw's scope.

## Key Claims

- [fact] [[FreeSoftwareFoundation]] — announced on 2024-10-22 that it is preparing a statement of criteria to determine when a machine-learning application is free
- [fact] [[FreeSoftwareFoundation]] — stated that the criteria are being drafted by a working group of FSF board members, staff, and management that consulted external experts
- [fact] [[FreeSoftwareFoundation]] — stated that serious work toward a unanimous conclusion began in May 2024 and has concluded, with the working group now drafting the exact definition text
- [analysis] [[FreeSoftwareFoundation]] — describes machine-learning applications as only partially software, since each also includes model parameters produced by training
- [analysis] [[FreeSoftwareFoundation]] — argues that training data is not the "source code" of model parameters in the usual sense, because parameters are not a translation of anything a human author wrote
- [analysis] [[FreeSoftwareFoundation]] — explains that in practice users study and adapt a machine-learning application by running it over different prompt data, analyzing its training data, and retraining it, rather than by editing parameters directly
- [fact] [[FreeSoftwareFoundation]] — stated that all software in a free machine-learning application must grant every user the four freedoms, covering both the training software and the inference software
- [fact] [[FreeSoftwareFoundation]] — stated that it cannot call a machine-learning application free unless all of its [[TrainingData]] and the related processing scripts respect the four freedoms
- [analysis] [[FreeSoftwareFoundation]] — holds that granting the four freedoms may require the release to include the model parameters, with users permitted to use and redistribute the parameters and modified versions of them
- [fact] [[FreeSoftwareFoundation]] — stated that machine-learning applications that do not offer the four freedoms to all users are nonfree even if their software components are free
- [analysis] [[FreeSoftwareFoundation]] — allows that some nonfree machine-learning applications may have valid moral reasons for withholding training data, citing personal medical data as the example
- [analysis] [[FreeSoftwareFoundation]] — holds that using such a nonfree application could be ethically excusable if it does a job vital to society, such as diagnosing disease or injury
- [fact] [[FreeSoftwareFoundation]] — set two conditions for considering that use just: the component software must be free, and the application must be distributed in a form that supports incremental training or retraining from scratch

## Key Quotes

> "ML applications that do not offer the four freedoms to all users are, by definition, nonfree, even if their software components are free." — [[FreeSoftwareFoundation]]

> "[W]e believe that we cannot say a ML application is free unless all its training data and the related scripts for processing it respect all users, following the four freedoms." — [[FreeSoftwareFoundation]]

> "It may be that some nonfree ML have valid moral reasons for not releasing training data, such as personal medical data." — [[FreeSoftwareFoundation]]

## Connections

- cites: [[FreeSoftwareFoundation]] — the FSF's own announcement of its free machine-learning application criteria
- references: [[TrainingData]] — the FSF requires raw training data and processing scripts to respect the four freedoms
- references: [[OpenSourceAI]] — the FSF frames freedom for machine-learning systems in terms of the same four freedoms
- references: [[OpenWeights]] — the FSF says a free release may need to include the model parameters with use and redistribution rights
