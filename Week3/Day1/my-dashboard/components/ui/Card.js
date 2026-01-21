export default function Card({ children, title, footer, variant = 'default', className = '' }) {
  const variants = {
    default: 'bg-white border border-gray-200',
    primary: 'bg-blue-500 text-white',
    success: 'bg-green-500 text-white',
    warning: 'bg-yellow-400 text-white',
    danger: 'bg-red-500 text-white'
  };
  
  return (
    <div className={`rounded-lg shadow-md overflow-hidden ${variants[variant]} ${className}`}>
      {title && (
        <div className={`px-6 py-4 border-b ${variant === 'default' ? 'border-gray-200' : 'border-white/20'}`}>
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      )}
      <div className="px-6 py-4">
        {children}
      </div>
      {footer && (
        <div className={`px-6 py-3 border-t ${variant === 'default' ? 'bg-gray-50 border-gray-200' : 'border-white/20'}`}>
          {footer}
        </div>
      )}
    </div>
  );
}