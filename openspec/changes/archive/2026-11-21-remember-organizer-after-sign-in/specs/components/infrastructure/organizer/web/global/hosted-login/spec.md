# Spec Delta

## MODIFIED Requirements

### Requirement: Every console sign-in names one Organization

The organizer console SHALL start every sign-in tied to exactly one Organizer's Organization and SHALL never start a sign-in that names none, because such a sign-in matches the fan account of a person whose fan and Organizer emails are the same. After a sign-in to an Organization admits the member, the console SHALL remember that Organization on the device and name it in the next sign-in there, until a later sign-in admits the member to another. An Organization named only by an address whose sign-in did not admit the member SHALL NOT be remembered and SHALL NOT replace the remembered one. The sign-in screen SHALL ask for the email alone: it SHALL show no domain or other text after the email field, since people type their whole email.

#### Scenario: Owner whose email is also a fan account

- **WHEN** the owner of `xx-records`, whose fan account has the same email, opens `https://organizer.liverty-music.app/?org=xx-records` and types that email
- **THEN** they sign in with the passkey of their identity in xx-records' Organization, shown as `<email> (xx-records)`, not with the fan account

#### Scenario: Device that remembers no Organization

- **WHEN** the console is opened on a device with no remembered Organization and no Organization in its address
- **THEN** no sign-in starts and the find-organizer screen is shown

#### Scenario: Link to an Organizer that does not exist

- **WHEN** someone opens `https://organizer.liverty-music.app/?org=gone-records` on a device with no remembered Organization, the sign-in does not admit them, and they then open the console without the link
- **THEN** no sign-in starts and the find-organizer screen is shown

#### Scenario: Failed link keeps the remembered Organization

- **WHEN** an owner whose device remembers xx-records' Organization opens `https://organizer.liverty-music.app/?org=gone-records`, that sign-in does not admit them, and they then open the console without the link
- **THEN** the sign-in for xx-records' Organization starts

#### Scenario: Sign-in screen asks for the email alone

- **WHEN** the console opens the sign-in for `xx-records`
- **THEN** the email field shows nothing after it, such as `@xx-records.auth.liverty-music.app`, and the whole typed email signs the owner in
