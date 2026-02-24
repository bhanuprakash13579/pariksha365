import React, { useState } from 'react';
import { View, Text, ScrollView, Dimensions } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import { styles, COLORS } from '../../styles/theme';
import { Ionicons } from '@expo/vector-icons';

const screenWidth = Dimensions.get("window").width;

export default function AnalyticsScreen({ navigation }: any) {
    // Dummy data to showcase the chart
    const data = {
        labels: ["Polity", "Reason", "English", "Apti"],
        datasets: [
            {
                data: [60, 85, 40, 92] // Accuracy percentages
            }
        ]
    };

    const chartConfig = {
        backgroundGradientFrom: "#ffffff",
        backgroundGradientTo: "#ffffff",
        color: (opacity = 1) => `rgba(249, 115, 22, ${opacity})`,
        labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
        strokeWidth: 2,
        barPercentage: 0.5,
        fillShadowGradientFrom: COLORS.primary,
        fillShadowGradientFromOpacity: 0.8,
        fillShadowGradientTo: COLORS.primary,
        fillShadowGradientToOpacity: 0.8,
        useShadowColorFromDataset: false
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.contentPadAlt}>
                {/* Nudge Banner */}
                <View style={[styles.infoBox, { backgroundColor: '#fff7ed', borderColor: '#fed7aa', flexDirection: 'row', alignItems: 'center' }]}>
                    <Ionicons name="bulb-outline" size={24} color={COLORS.primary} />
                    <Text style={[styles.infoText, { color: '#c2410c', marginLeft: 10, flex: 1, lineHeight: 20 }]}>
                        Focus Alert: Your accuracy in English is <Text style={{ fontWeight: 'bold' }}>40%</Text>. Watch grammar video lectures before re-attempting mocks!
                    </Text>
                </View>

                <Text style={[styles.sectionTitle, { marginTop: 25 }]}>Subject Accuracy (%)</Text>
                <View style={[styles.chartWrapper, { padding: 0, paddingRight: 15, paddingTop: 15 }]}>
                    <BarChart
                        style={{ marginVertical: 8, borderRadius: 16 }}
                        data={data}
                        width={screenWidth - 40}
                        height={240}
                        yAxisLabel=""
                        yAxisSuffix="%"
                        chartConfig={chartConfig}
                        verticalLabelRotation={0}
                        fromZero={true}
                        showValuesOnTopOfBars={true}
                    />
                </View>

                {/* Subject Breakdown Detailed */}
                <Text style={[styles.sectionTitle, { marginTop: 25 }]}>Detailed Breakdown</Text>
                {data.labels.map((label, idx) => (
                    <View key={label} style={[styles.card, { paddingVertical: 12, marginBottom: 10 }]}>
                        <Text style={styles.cardTitle}>{label === 'Reason' ? 'Reasoning' : label === 'Apti' ? 'Aptitude' : label}</Text>
                        <Text style={[styles.scoreText, { fontSize: 16, color: data.datasets[0].data[idx] > 50 ? COLORS.success : COLORS.error }]}>
                            {data.datasets[0].data[idx]}%
                        </Text>
                    </View>
                ))}

            </View>
        </ScrollView>
    );
}
