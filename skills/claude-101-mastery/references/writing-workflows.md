# Writing & Communication Tool Workflows

## 1. Email Drafting (`draft_email`)

**Trigger:** User asks to write, draft, or review an email.

**Call:** `draft_email(context, tone, output_format)`

**Workflow:**
1. Use `text_analysis.formality_score` to calibrate writing formality
2. Use `tone_guide.vocabulary` — weave these phrases naturally into the draft
3. Use `tone_guide.avoid` — ensure none appear in the output
4. Use `text_analysis.structure` — verify greeting/CTA/closing are present
5. Use `text_analysis.readability` — adjust sentence complexity to match Flesch target
6. Write the email using `sections` as structural guide (not verbatim)
7. Present `pre_send_checklist` to the user at the end

**Quality check:** Re-read and verify formality matches the computed score range.

## 2. Blog Post Planning (`draft_blog_post`)

**Trigger:** User wants to plan, outline, or write a blog post.

**Call:** `draft_blog_post(topic, target_words, style)`

**Workflow:**
1. Follow `outline` section structure with exact `target_words` per section
2. Match `style_guide` voice, sentence length, and examples-per-section
3. Include `seo_fields` focus keyword in headings and body; use the slug for URLs
4. Ensure `topic_analysis.primary_keywords` appear in headings and body
5. Write within the `readability_target` Flesch score range
6. Verify `heading_validation` shows no issues
7. Address each item in `content_gaps`
8. Present `seo_fields` for CMS configuration

## 3. Meeting Notes (`parse_meeting_notes`)

**Trigger:** User pastes raw meeting notes or transcript.

**Call:** `parse_meeting_notes(raw_notes, output_format)`

**Workflow:**
1. List all `attendees`
2. Present each `action_items` entry with owner, task, and deadline
3. Highlight all `decisions`
4. Organize notes by `topics_discussed`
5. Summarize using `metrics` (duration, action count, decision count)
6. Flag any action items with owner "unassigned" — ask the user who should own them
7. Format into a clean structured summary for team distribution

## 4. Social Media (`format_social_content`)

**Trigger:** User wants to create social media posts.

**Call:** `format_social_content(text, platform, include_hashtags)`

**Workflow:**
1. Check `within_limit` — if false, the content MUST be shortened
2. If text needs splitting, use `chunks` (pre-numbered for threads)
3. Append relevant `hashtags` (or weave them in naturally)
4. Check `engagement_signals` — if `has_question` is false, consider adding one; if `hook_strength` is weak, rewrite the first line
5. Rewrite content optimizing for the platform while keeping the user's message

## 5. Technical Documentation (`scaffold_tech_doc`)

**Trigger:** User needs a README, API doc, RFC, ADR, runbook, or other technical doc.

**Call:** `scaffold_tech_doc(doc_type, title, sections, content)`

**Workflow:**
1. Follow `sections` exact structure (required vs optional)
2. Incorporate each `best_practices` item into the writing
3. Use `template` as starting skeleton, replace all `[placeholders]`
4. Share `effort_estimate` with user for planning
5. If `analysis.code_structure` present — reference extracted functions/classes
6. If `analysis.completeness` present (README) — address every item in `missing` list

## 6. Creative Writing (`structure_story`)

**Trigger:** User wants to write fiction, plan a story, or analyze existing text.

**Call:** `structure_story(genre, elements, structure, text)`

**Workflow:**
1. Follow `beats` with their word targets and tension levels
2. Ensure writing follows the `tension_curve` emotional arc
3. Use `character_arc_template` as guide for character development
4. Incorporate at least 3 of the `genre_conventions`
5. If `text_analysis` present:
   - Fix any beats marked "slow" or "fast" in `pacing`
   - Adjust `dialogue.ratio` if too heavy/light for genre
   - Add more transitions if `scene_transitions.avg_scene_words` is very high
   - Balance `character_mentions.distribution` screen time
