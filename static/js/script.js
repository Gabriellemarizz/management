document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('click', () => {
    alert(`Você clicou em "${btn.textContent}"`);
  });
});
document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('mouseover', () => {
    btn.style.backgroundColor = 'lightblue';
  });
  
  btn.addEventListener('mouseout', () => {
    btn.style.backgroundColor = '';
  });
});