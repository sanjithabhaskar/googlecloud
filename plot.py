import matplotlib.pyplot as plt

# Given data
x = [0.657, -0.1818, -0.1197, 0.9543, 0.1903, 1.1411, 1.6878, 1.4394, 0.9467, 0.2607, -0.1655, 0.8891, 0.1827, 0.3758, 0.3089, 0.1897]
y = [0.20462051904761902, 0.1645351428571429, 0.31345325714285716, 1.2706895190476184, 0.40812393333333347, 1.007343595238095, 1.0609753666666668, 1.1211348547619047, 1.076157488095238, 0.21260480952380953, 0.24952416666666669, 0.4704655095238095, 0.33987582380952375, 0.11520186111111108, 0.20036984523809523, 0.20166563333333337]

# Create scatter plot
plt.scatter(x, y, color='blue', label='Data')

# Add labels and title
plt.xlabel('Calculated Data (x)')
plt.ylabel('Predicted Data (y)')
plt.title('Scatter Plot of Calculated vs Predicted Data')

# Add legend
plt.legend()

# Show plot
plt.grid(True)
plt.show()
