export default function Profile() {
  return (
    <div className="content-inner" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', backgroundColor: '#f9f9f9'}}>
      <div style={{fontSize: '5rem', marginBottom: '20px'}}>👤</div>
      <h1 style={{color: '#22252a', fontSize: '2.5rem', marginBottom: '10px'}}>User Profile</h1>
      <p style={{color: '#888', fontStyle: 'italic', fontSize: '1.2rem'}}>Manage your preferences, saved restaurants, and account settings.<br/>(This module is under construction)</p>
    </div>
  );
}
