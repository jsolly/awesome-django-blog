---
slug: web3-notes-personal-reference
title: "Web3 Notes: A Personal Reference"
category: resources
description: Keep track of important web3 topics with these personal notes. Use them as a reference and stay informed about the latest developments in the world of web3.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/web3Image.webp
legacyImage: post_metaimgs/web3Image.webp
imageAlt: John Solly Headshot
imageAttribution: "Stable Diffusion using this prompt: Web3, logo, crypto, Etherum, coin, blockchain"
imageWidth: 768
imageHeight: 768
published: "2023-01-06T17:53:07.256Z"
updated: "2023-01-06T17:53:07.256Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Keep track of important web3 topics with these personal notes. Use them as a reference and stay informed about the latest developments in the world of web3.</p>
legacyId: 110
related:
  - how-I-present-portfolio-projects-to-impress
  - Adding-views-likes-to-posts
  - compress-minify-assets-69-percent-faster-page-load
---

## Intro

Welcome to my latest blog post where I will be sharing my personal notes on some of the most important web3 topics. As someone who is constantly keeping an eye on the latest developments in the world of web3, I understand the importance of having a reliable reference to turn to. In this post, I have compiled a list of notes that I have collected over time, covering various web3 topics such as blockchain, smart contracts, decentralized finance, and more. These notes will not only help you stay informed about the latest trends and advancements in the field but also serve as a useful resource to refer back to. Whether you're a beginner or an experienced developer, this post is for anyone looking to stay up-to-date with the world of web3. So, without further ado, let's dive in!

## Table of Contents

<ol><li><a href="#web3-terms">Web3 Terms</a><ul><li><a href="#tableland">Tableland</a></li><li><a href="#estuary">Estuary</a></li><li><a href="#cid">CID</a></li><li><a href="#kyc">KYC</a></li><li><a href="#staking">Staking</a></li><li><a href="#por-proof-of-replication">PoR (Proof of Replication)</a></li><li><a href="#post-proof-of-spacetime">PoSt (Proof of Spacetime)</a></li><li><a href="#filecoin">Filecoin</a></li><li><a href="#chunking">Chunking</a></li><li><a href="#committed-capacity">Committed capacity</a></li><li><a href="#kademlia-algorithim-distributed-hash-tables-dhts">Kademlia Algorithm (Distributed Hash Tables) DHTs</a></li><li><a href="#reproviding">Reproviding</a></li><li><a href="#porep">PoRep</a></li><li><a href="#on-chain/off-chain">On-chain/off-chain</a></li><li><a href="#filecoin-plus-fil+">Filecoin Plus (FIL+)</a></li></ul></li><li><a href="#foam-mapping">Foam Mapping</a><ul><li><a href="#summary">Summary</a></li><li><a href="#anchors">Anchors</a></li><li><a href="#verifiers">Verifiers</a></li><li><a href="#pol-proof-of-location">PoL (Proof of Location)</a></li><li><a href="#crypto-spatial-coordinate-standard">Crypto Spatial Coordinate Standard</a></li><li><a href="#spatial-index">Spatial Index</a></li></ul></li></ol>

<h2 id="web3-terms">Web3 Terms</h2>

<h3 id="tableland">Tableland</h3>

<p id="tableland">Web3 native relational tables. Token enabled protocol.</p>

<h3 id="estuary">Estuary</h3>

<p id="estuary">Communication and storage broker between client and storage provider. Uses Barge CLI to upload, chunk files.</p>

<h3 id="cid">CID</h3>

<p id="cid">A CID is a single identifier that contains both a cryptographic hash and a codec, which holds information about how to interpret that data. Codecs encode and decode data in certain formats.</p>

<h3 id="kyc">KYC</h3>

<p id="kyc">Know your customer</p>

<h3 id="staking">Staking</h3>

<p id="staking">Locking up coins to earn interest income</p>

<h3 id="por-proof-of-replication">PoR (Proof of Replication)</h3>

<p id="por-proof-of-replication">Run once at the beginning of a deal to proof that the miner has stored the data.</p>

<h3 id="post-proof-of-spacetime">PoSt (Proof of Spacetime)</h3>

A regular check to make sure the data is       
still being stored.

<pre><code class="language-bash">$ cat ~/.ipfs/config
$ ipfs dht findprovs &lt;CID&gt;
// Get peers that have hashed the node that is
hosting the data</code></pre>

<h3 id="filecoin">Filecoin</h3>

<p id="filecoin">“Blockchain managed distributed storage system”</p>

<h3 id="chunking">Chunking</h3>

<p id="chunking">Chunk size determines block size.</p>

<h3 id="committed-capacity">Committed Capacity</h3>

Sectors with no deals are called ‘committed capacity sectors’...upgrading capacity currently       
involves resealing. The maximum sector lifetime is 18 months...(Is this still true?)

<h3 id="kademlia-algorithim-distributed-hash-tables-dhts">Kademlia Algorithm (Distributed Hash Tables) DHTs</h3>

Peer to Peer discovery of content. The peers who are most similar to the CID are told about its existence (default is 20 peers).

<h3 id="reproviding">Reproviding</h3>

Every 12 hours, you are required to ‘rebroadcast’ to the network that you can still provide this       
content. This keeps data ‘fresh’ incase a node goes down.

<h3 id="porep">PoRep</h3>

Computation intensive process that results in a unique encoding of the       
secret. Then a proof and a SNARK is run on the proof to compress it.

<h3 id="on-chain/off-chain">On-chain/off-chain</h3>

On-chain actions are those that change the state of the tree and the blockchain and       
interact with the Filecoin VM. Off chain actions are those that do not interact with the Filecoin VM.

<h3 id="filecoin-plus-fil+">Filecoin Plus (FIL+)</h3>

\- 10x power - 10x collateral Notaries hand out data caps

<h2 id="foam-mapping">FOAM Mapping</h2>

<h3 id="summary">Summary</h3>

<p id="summary">FOAM (FOAM Map) is a decentralized, open-source map for geographic information that is built on the Ethereum blockchain. It allows users to contribute and verify information about geographical locations, creating a crowdsourced and constantly updating map. FOAM utilizes a token-based system to incentivize users to contribute and verify accurate information, and to deter users from adding false or misleading information to the map. The goal of FOAM is to create a more reliable and accurate map that can be used in a variety of contexts, including navigation, urban planning, and emergency response.</p>

<h3 id="anchors">Anchors</h3>

<p id="anchors">In the FOAM map, anchors are physical devices that are placed at specific locations and are used to anchor location information to the Ethereum blockchain. Anchors can be used to verify the accuracy of location data on the FOAM map.</p>

<h3 id="verifiers">Verifiers</h3>

Verifiers are users of the FOAM map who are responsible for verifying the accuracy of the location data on the map. Verifiers can earn rewards in the form of FOAM tokens for verifying the accuracy of location data. Verifiers can also challenge the accuracy of location data that they believe to be incorrect, and can earn additional rewards if their challenges are successful.

FOAM uses a system of proof-of-stake and reputation to determine which users are eligible to serve as verifiers. In general, users with a higher stake in the FOAM map and a good reputation are more likely to be selected as verifiers.

<h3 id="pol-proof-of-location">PoL (Proof of Location)</h3>

In the context of FOAM, Proof of Location (PoL) is a protocol that allows users to prove the location of a specific point on the map. This can be done using anchors, which are physical devices placed at specific locations that can be used to anchor location information to the Ethereum blockchain. When an anchor broadcasts its location, it creates a "Proof of Location" that can be verified by other users on the FOAM map.

PoL is a key component of the FOAM map, as it allows users to verify the accuracy of location data on the map and helps to ensure that the map is reliable and up-to-date. By using PoL, FOAM aims to create a more accurate and trustworthy map that can be used in a variety of contexts, including navigation, urban planning, and emergency response.

<h3 id="crypto-spatial-coordinate-standard">Crypto Spatial Coordinate Standard</h3>

<h3 id="spatial-index">Spatial Index</h3>

<p id="spatial-index">&nbsp;</p>

<h2 id="spatial-index">Web3 Finance</h2>

<p id="spatial-index">Whenever you purchase cryptocurrency with fiat money (USD, Pounds, Euros), you may encounter some fees. For example, coinbase charges an exchange rate where they place a margin between the current rate going in the marketplace</p>

<p id="spatial-index">1 - Consumer exchange rate current market price of the coin...bit worse than the price on 'Coinbase Pro' platform. It's a margin (~0.5%)</p>

<p id="spatial-index">2 Coinbase fee - Variable fee based on</p>

<ul><li id="spatial-index">Region, amount to be purchased, method of payment (Debit card, credit card, bank account)</li></ul>

<p id="spatial-index">&nbsp;</p>
